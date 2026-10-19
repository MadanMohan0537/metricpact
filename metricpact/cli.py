import argparse, json
from pathlib import Path
from .benchmark import run_benchmark
from .data import ORDERS, ORDER_ITEMS
from .engine import GrainError, MetricPact, check_join_grain

def build_report():
    engine = MetricPact()
    examples = [engine.ask(q).to_dict() for q in ("gross sales by region", "net sales by month", "sales")]
    try:
        check_join_grain(ORDERS, ORDER_ITEMS, "order_id")
        grain = {"unsafe_join_blocked": False}
    except GrainError as exc:
        grain = {"unsafe_join_blocked": True, "reason": str(exc), "safe_alternative": "Aggregate order_items to order_id before joining."}
    return {"product": "MetricPact", "benchmark": run_benchmark(), "grain_experiment": grain, "examples": examples}

def main():
    parser = argparse.ArgumentParser(description="Run the MetricPact evidence demo")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = build_report()
    rendered = json.dumps(report, indent=2)
    if args.output: args.output.write_text(rendered + "\n")
    print(rendered)

if __name__ == "__main__": main()
