# MetricPact

**Ask governed business questions without turning natural language into unaudited SQL.**

MetricPact is a dependency-free Python MVP that maps questions onto a semantic metrics layer,
shows the generated SQL and assumptions, enforces a scan budget, detects grain-unsafe joins,
and returns reconciliation evidence with every verified answer.

> AI PM Project Lab traceability: project 16, originally “Ask the Warehouse.”

## Why this exists

Natural-language analytics can produce plausible but wrong numbers when “sales” has multiple
definitions or a one-to-many join duplicates facts. MetricPact treats clarification, governance,
and verification as product behavior—not post-hoc warnings.

## Shipped MVP

- Five allow-listed metrics: gross sales, net sales, order count, customer count and AOV.
- Region/month grouping and deterministic filters over reproducible synthetic data.
- Ambiguity gate: bare “sales” and “revenue” are not guessed.
- SQL and assumptions shown for every verified query; user text is never interpolated into SQL.
- Scan-row budget with a blocked outcome before execution.
- Post-execution reconciliation evidence.
- **Prioritized extension shipped:** declared grains plus cardinality preflight reject unsafe
  order-to-item joins and permit explicitly pre-aggregated alternatives.
- 20-question benchmark, 16 unit tests and Python 3.11–3.13 CI.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m metricpact.cli --output evidence.json
python -m unittest discover -s tests -v
```

No service, credential, network connection or paid API is required.

## Example

Question: `net sales by month`

```sql
SELECT month, SUM(amount - refund) AS net_sales
FROM governed.orders
GROUP BY month;
```

The response includes grouped values, UTC/currency assumptions, the estimated six-row scan,
the configured limit, semantic-layer version and a reconciled total. Asking only `sales`
returns `clarify` and requests a gross-versus-net choice.

## Architecture

```mermaid
flowchart LR
  A[Question] --> B[Semantic planner]
  B --> C[Cost and grain gates]
  C --> D[Deterministic executor]
  D --> E[Answer plus evidence]
```

The boundaries are intentionally narrow. See [method and limitations](docs/METHOD.md) and the
[rigorous feature backlog](docs/BACKLOG.md).

## Evidence and honest scope

`metricpact.cli` runs three examples, the 20-case benchmark and the unsafe-join experiment.
The expected local benchmark is 20/20, and the naive order-to-item join is expected to be blocked.
Those results establish deterministic fixture behavior only—not production accuracy on arbitrary
language or warehouse schemas.

## Repository map

```text
metricpact/      engine, governed fixture, benchmark and CLI
tests/           behavioral and safety tests
docs/            method, limitations and current backlog
.github/         reproducible CI and evidence artifact
```

## License

MIT
