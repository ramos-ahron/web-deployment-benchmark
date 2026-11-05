#!/usr/bin/env python3
"""Cut continuous sampler files into per-run files using each run's metadata.txt times.
usage (repo root): python monitoring/split_continuous.py web=mon_web_*.csv db=mon_db_*.csv load=mon_load_*.csv
(several files per role: comma-separate them, e.g. web=a.csv,b.csv; a shell glob also works if quoted) [--results results] [--pad 5]
Writes results/<run_id>/<run_id>_<role>.csv (existing files are not overwritten).
analyze.py later trims to the exact measure phase, so --pad seconds of slack around start_utc/end_utc is fine."""
import sys
from pathlib import Path
import pandas as pd

args = sys.argv[1:]
res = Path(args[args.index("--results") + 1]) if "--results" in args else Path("results")
pad = float(args[args.index("--pad") + 1]) if "--pad" in args else 5.0
srcs = dict(a.split("=", 1) for a in args if "=" in a and not a.startswith("--"))
if not srcs: sys.exit(__doc__)
import glob
data = {role: pd.concat([pd.read_csv(f) for pat in p.split(",") for f in sorted(glob.glob(pat))]).sort_values("ts_epoch")
        for role, p in srcs.items()}
for d in sorted(p for p in res.iterdir() if p.is_dir() and (p / "metadata.txt").exists()):
    m = dict(l.split("=", 1) for l in (d / "metadata.txt").read_text().splitlines() if "=" in l)
    t0 = pd.Timestamp(m["start_utc"]).timestamp() - pad
    t1 = pd.Timestamp(m["end_utc"]).timestamp() + pad
    for role, df in data.items():
        out = d / f"{m['run_id']}_{role}.csv"
        if out.exists(): print(f"skip {out} (exists)"); continue
        part = df[(df.ts_epoch >= t0) & (df.ts_epoch <= t1)]
        part.to_csv(out, index=False)
        print(f"{out}: {len(part)} rows" + ("  <-- NO DATA" if part.empty else ""))
