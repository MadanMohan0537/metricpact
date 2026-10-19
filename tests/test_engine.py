import unittest
from metricpact.benchmark import run_benchmark
from metricpact.data import ORDERS, ORDER_ITEMS
from metricpact.engine import GrainError, MetricPact, Status, assert_unique, check_join_grain

class EngineTests(unittest.TestCase):
    def setUp(self): self.engine = MetricPact()
    def test_gross_total(self): self.assertEqual(self.engine.ask("gross sales").rows[0]["gross_sales"], 700)
    def test_net_total(self): self.assertEqual(self.engine.ask("net sales").rows[0]["net_sales"], 620)
    def test_orders(self): self.assertEqual(self.engine.ask("orders").rows[0]["order_count"], 6)
    def test_customers(self): self.assertEqual(self.engine.ask("customers").rows[0]["customer_count"], 4)
    def test_aov(self): self.assertEqual(self.engine.ask("average order value").rows[0]["average_order_value"], 116.67)
    def test_ambiguous_sales(self): self.assertEqual(self.engine.ask("sales").status, Status.CLARIFY)
    def test_region_group(self): self.assertEqual(len(self.engine.ask("gross sales by region").rows), 3)
    def test_region_filter(self): self.assertEqual(self.engine.ask("net sales in West").rows[0]["net_sales"], 150)
    def test_month_filter(self): self.assertEqual(self.engine.ask("orders 2026-02").rows[0]["order_count"], 2)
    def test_sql_is_transparent(self): self.assertIn("SUM(amount - refund)", self.engine.ask("net sales").sql)
    def test_assumptions_exposed(self): self.assertIn("Calendar dates use UTC", self.engine.ask("orders").assumptions)
    def test_cost_block(self): self.assertEqual(MetricPact(max_scan_rows=2).ask("orders").status, Status.BLOCKED)
    def test_grain_mismatch_blocked(self):
        with self.assertRaises(GrainError): check_join_grain(ORDERS, ORDER_ITEMS, "order_id")
    def test_preaggregation_allowed(self): self.assertEqual(check_join_grain(ORDERS, ORDER_ITEMS, "order_id", preaggregated=True)["cardinality"], "many-to-one")
    def test_duplicate_declared_grain(self):
        with self.assertRaises(GrainError): assert_unique([{"id": 1}, {"id": 1}], ("id",), "bad")
    def test_benchmark(self): self.assertEqual(run_benchmark()["accuracy"], 1.0)

if __name__ == "__main__": unittest.main()
