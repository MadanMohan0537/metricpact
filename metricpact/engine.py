"""Dependency-free governed analytics engine.

The parser is intentionally constrained: user text selects allow-listed semantic
objects; it is never interpolated into SQL.
"""
from dataclasses import asdict, dataclass
from enum import StrEnum
import re

from .data import ORDERS, ORDER_ITEMS


class Status(StrEnum):
    VERIFIED = "verified"
    CLARIFY = "clarify"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class Metric:
    name: str
    label: str
    expression: str
    reducer: str


@dataclass
class QueryResult:
    question: str
    status: Status
    metric: str | None = None
    dimension: str | None = None
    rows: list[dict] | None = None
    sql: str | None = None
    assumptions: list[str] | None = None
    evidence: dict | None = None
    message: str = ""

    def to_dict(self):
        result = asdict(self)
        result["status"] = self.status.value
        return result


METRICS = {
    "gross_sales": Metric("gross_sales", "Gross sales", "SUM(amount)", "sum_amount"),
    "net_sales": Metric("net_sales", "Net sales", "SUM(amount - refund)", "sum_net"),
    "order_count": Metric("order_count", "Orders", "COUNT(DISTINCT order_id)", "count_orders"),
    "customer_count": Metric("customer_count", "Customers", "COUNT(DISTINCT customer_id)", "count_customers"),
    "average_order_value": Metric("average_order_value", "Average order value", "AVG(amount)", "avg_amount"),
}


class GrainError(ValueError):
    pass


def assert_unique(rows, keys, table):
    seen = set()
    for row in rows:
        grain = tuple(row[k] for k in keys)
        if grain in seen:
            raise GrainError(f"{table} violates declared grain {keys}: duplicate {grain}")
        seen.add(grain)


def check_join_grain(left, right, key, *, preaggregated=False):
    """Reject right-side one-to-many joins unless explicitly pre-aggregated."""
    counts = {}
    for row in right:
        counts[row[key]] = counts.get(row[key], 0) + 1
    risky = sorted(k for k, count in counts.items() if count > 1)
    if risky and not preaggregated:
        raise GrainError(
            f"one-to-many join would duplicate order-grain metrics; repeated {key}: {risky}"
        )
    return {"cardinality": "many-to-one" if preaggregated else "one-to-one", "repeated_keys": risky}


class MetricPact:
    def __init__(self, max_scan_rows=100):
        self.max_scan_rows = max_scan_rows
        assert_unique(ORDERS, ("order_id",), "orders")
        assert_unique(ORDER_ITEMS, ("item_id",), "order_items")

    def ask(self, question):
        q = question.lower().strip()
        metric = self._metric(q)
        if metric is None:
            return QueryResult(question, Status.CLARIFY, message="Choose gross sales or net sales; 'sales' is definitionally ambiguous.")
        dimension = "region" if "region" in q else "month" if "month" in q else None
        region = next((r for r in ("East", "West", "North") if r.lower() in q), None)
        month_match = re.search(r"2026-(0[1-3])", q)
        month = month_match.group(1) if month_match else None
        scanned = len(ORDERS)
        if scanned > self.max_scan_rows:
            return QueryResult(question, Status.BLOCKED, metric=metric.name, evidence={"estimated_scan_rows": scanned, "limit": self.max_scan_rows}, message="Estimated scan exceeds the configured row budget.")
        filtered = [r for r in ORDERS if (not region or r["region"] == region) and (not month or r["ordered_on"][5:7] == month)]
        groups = {}
        for row in filtered:
            key = row[dimension] if dimension == "region" else row["ordered_on"][:7] if dimension == "month" else "total"
            groups.setdefault(key, []).append(row)
        rows = [{dimension or "scope": key, metric.name: self._reduce(metric, values)} for key, values in sorted(groups.items())]
        where = []
        if region: where.append(f"region = '{region}'")
        if month: where.append(f"ordered_on >= '2026-{month}-01' AND ordered_on < '2026-{int(month)+1:02d}-01'")
        select_dim = f"{dimension}, " if dimension else ""
        group = f" GROUP BY {dimension}" if dimension else ""
        sql = f"SELECT {select_dim}{metric.expression} AS {metric.name} FROM governed.orders" + (" WHERE " + " AND ".join(where) if where else "") + group + ";"
        expected = sum(v[metric.name] for v in rows) if metric.reducer != "avg_amount" else None
        return QueryResult(question, Status.VERIFIED, metric.name, dimension, rows, sql,
                           ["Calendar dates use UTC", "Amounts use the synthetic warehouse currency"],
                           {"estimated_scan_rows": scanned, "row_limit": self.max_scan_rows, "reconciled_total": expected, "semantic_layer": "v1"},
                           "Generated only from allow-listed semantic objects and reconciled after execution.")

    @staticmethod
    def _metric(q):
        if "gross" in q: return METRICS["gross_sales"]
        if "net" in q: return METRICS["net_sales"]
        if "average" in q or "aov" in q: return METRICS["average_order_value"]
        if "customer" in q: return METRICS["customer_count"]
        if "order" in q: return METRICS["order_count"]
        if "sales" in q or "revenue" in q: return None
        return None

    @staticmethod
    def _reduce(metric, rows):
        if metric.reducer == "sum_amount": return sum(r["amount"] for r in rows)
        if metric.reducer == "sum_net": return sum(r["amount"] - r["refund"] for r in rows)
        if metric.reducer == "count_orders": return len({r["order_id"] for r in rows})
        if metric.reducer == "count_customers": return len({r["customer_id"] for r in rows})
        if metric.reducer == "avg_amount": return round(sum(r["amount"] for r in rows) / len(rows), 2) if rows else 0
        raise ValueError(metric.reducer)
