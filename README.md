# Governed Metric Query Engine

[![CI](https://github.com/MadanMohan0537/governed-metric-query-engine/actions/workflows/ci.yml/badge.svg)](https://github.com/MadanMohan0537/governed-metric-query-engine/actions/workflows/ci.yml)

**Answer a question from an allow-listed metrics layer. Ambiguous "sales" or "revenue" returns `clarify` instead of a guessed metric. A separate preflight rejects an order-to-item join that would duplicate order-grain amounts.**

A Python MVP with no third-party runtime dependencies. The package and the CLI are still called `metricpact`.

## Problem and who it's for

When people ask a data tool for "sales" or "revenue", they often get a number that looks right but isn't. "Sales" can mean gross or net, and a one-to-many join (orders to order items) can silently duplicate order-level amounts. The people who get hurt are analysts, analytics engineers, and the product or finance managers who act on the number without seeing the SQL.

This project treats clarification, a scan-row limit, and join safety as product behavior rather than as warnings after the fact.

## Approach

1. Map a question onto a small **semantic layer** of allow-listed metrics and dimensions. Arbitrary question text is not copied into SQL. The only question-derived tokens that appear in SQL are the allow-listed regions East, West, and North, and the months `2026-01`, `2026-02`, and `2026-03`.
2. If the question says "sales" or "revenue" without "gross" or "net", return `clarify` instead of picking a metric. A question that matches none of the allow-listed metrics returns that same `clarify` message. There is no separate "not understood" status.
3. Before computing a result, compare the fixture order count with a **scan-row budget**. Separately, declared grains are checked when the engine is constructed, and `check_join_grain` rejects a right-side one-to-many join unless the caller marks it pre-aggregated. That join check is not inside `ask()`.
4. Compute the result in process from the fixture rows. Return the SQL that describes the allow-listed query, the assumptions, semantic layer `v1`, and, for additive metrics, a reconciled total. The SQL string is not executed.

```mermaid
flowchart LR
  A[Question] --> B[Semantic planner]
  B --> C[Scan-row budget]
  C --> D[In-process fixture result]
  D --> E[Answer, SQL, and evidence]
```

## What exists today

- Five allow-listed metrics: gross sales, net sales, order count, customer count, and average order value (also matched by `aov`). Grouping is by region or by month when those words appear. If both appear, region is used. Filters are East, West, North, and months `2026-01` through `2026-03`.
- Ambiguity gate: "sales" and "revenue" return `clarify` with `Choose gross sales or net sales; 'sales' is definitionally ambiguous.`
- Every `verified` answer includes the generated SQL and the assumptions `Calendar dates use UTC` and `Amounts use the synthetic warehouse currency`. `clarify` and `blocked` answers do not.
- A scan-row budget. `ask()` compares `len(orders)` (6 in the fixture) with `max_scan_rows` (default 100) and returns `blocked` before computing rows when the count is over the limit. The bundled questions stay under the default limit. The unit test sets the limit to 2 to show the block.
- Grain checks. At construction, `orders` must be unique on `order_id` and `order_items` on `item_id`. The cardinality preflight rejects the naive order-to-item join with `one-to-many join would duplicate order-grain metrics; repeated order_id: ['o1']`. The CLI records the alternative `Aggregate order_items to order_id before joining.` Calling the preflight with `preaggregated=True` allows the join and labels it `many-to-one`.
- Evidence on `verified` answers: estimated scan rows, the row limit, semantic layer `v1`, and `reconciled_total`. That total is the sum of the grouped values just returned. It is `null` for average order value.
- A 20-question fixture benchmark. Each case checks status and metric name only, not the numeric value. The unit test requires that routing score to be 1.0.
- 16 unit tests in `tests/test_engine.py`. The workflow [`.github/workflows/ci.yml`](.github/workflows/ci.yml) runs those tests and `python -m metricpact.cli --output evidence.json` on Python 3.11, 3.12, and 3.13, and uploads `evidence.json`.

`python -m metricpact.cli --output evidence.json` writes two verified examples (`gross sales by region`, `net sales by month`), one `clarify` example (`sales`), the 20-case benchmark, and the unsafe-join experiment.

## How success would be measured

| Measure | Status |
|---|---|
| Numeric answers correct on real questions or a warehouse | Not yet measured |
| Share of ambiguous questions that get a clarifying question instead of a guess | Not yet measured |
| Grain-unsafe joins caught before execution outside this fixture | Not yet measured |
| Time for an analyst to trust or reject an answer | Not yet measured |

The 20-case benchmark is a routing regression check in the unit tests. No measurement results are committed in the repository (`evidence.json` is gitignored).

## Limitations

- The semantic layer is a small fixture: five metrics, six synthetic orders, seven item rows, and an in-process Python executor. It does not connect to a warehouse, and it does not run the SQL it returns.
- Questions are matched with keyword rules, not a language model. Wording outside the supported patterns receives the gross-versus-net `clarify` message.
- The scan budget is the fixture order count, not a warehouse cost estimate. Filters do not change the estimate.
- Join-grain rejection is a separate preflight. Asking a question does not apply it.
- The reconciled total sums the rows just produced. It is not a check against an independent source, and average order value has none.
- There is no authentication, multi-tenant access control, or query history.

See [docs/METHOD.md](docs/METHOD.md) and [docs/BACKLOG.md](docs/BACKLOG.md).

## Quick start

Requires Python 3.11+. The engine makes no network calls and needs no credentials or paid API.

```bash
git clone https://github.com/MadanMohan0537/governed-metric-query-engine.git
cd governed-metric-query-engine
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m unittest discover -s tests -v
python -m metricpact.cli --output evidence.json
```

## Deployment

Cloudflare Workers is the planned deploy target. This repository is not configured for Workers, and it is not deployed.

There is no `wrangler.toml`, Worker entry point, Worker name, or binding. `npx wrangler deploy` needs all of the following before it can run:

- a `wrangler.toml` with the Worker name and entry point
- a Worker entry point
- a way to run this Python package on Workers: Cloudflare Python Workers, or a JavaScript or TypeScript port

No Worker name is set here, so there is no live `workers.dev` URL to keep.

## Repository map

```text
metricpact/      engine, governed fixture, benchmark, and CLI
tests/           behavioral and safety tests
docs/            method, limitations, and backlog
.github/         CI workflow and evidence artifact upload
```

## License

MIT. See [LICENSE](LICENSE).
