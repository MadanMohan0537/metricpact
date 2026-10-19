# Method and evidence

MetricPact uses a closed semantic layer rather than free-form SQL generation. The MVP maps
phrases to five approved metrics and two dimensions, constructs SQL from identifiers owned by
the application, estimates a scan budget, executes against deterministic fixture rows, and
returns the SQL, assumptions and reconciliation value together.

The shipped grain extension declares `orders` at `order_id` and `order_items` at `item_id`.
Its preflight cardinality test finds two items for `o1`, so joining an order-level amount to
item rows is blocked. An explicit item aggregation to order grain changes the operation to a
many-to-one join and is allowed.

The benchmark contains 20 representative questions: direct metrics, grouping, filters,
synonyms and intentionally ambiguous “sales” requests. It tests routing/status, not language
understanding in the general case. The CLI emits machine-readable evidence for inspection.

## Limitations

- This is a portfolio MVP over six synthetic orders, not a database driver or production NL parser.
- Cost is represented by rows scanned; warehouses price bytes, slots and cache behavior differently.
- Full-fixture grain checks catch every duplicate here, but production sampling can miss rare keys.
- Reconciliation detects internal inconsistencies; it cannot prove upstream source correctness.
- Timezones, fiscal calendars, currencies, access control and differential privacy are not implemented.
