import argparse
import json
import os
from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analysis.data import ROOT, load_data
from analysis.metrics import cohort_retention, customer_segments, summarize

parser = argparse.ArgumentParser(description="Export all-data retail metrics and BI-ready tables.")
parser.add_argument("--data", type=Path, default=os.environ.get("DATA_DIR"))
parser.add_argument("--output", type=Path, default=ROOT / "exports")
args = parser.parse_args()
lines, counts = load_data(args.data)
args.output.mkdir(parents=True, exist_ok=True)
(args.output / "summary.json").write_text(json.dumps(summarize(lines), indent=2), encoding="utf-8")
lines.to_csv(args.output / "order_lines.csv", index=False)
customer_segments(lines, lines.order_date.max() + pd.Timedelta(days=1)).to_csv(args.output / "customer_segments.csv", index=False)
cohort_retention(lines).to_csv(args.output / "cohort_retention.csv")
print(f"Exported retail reports to {args.output}")
