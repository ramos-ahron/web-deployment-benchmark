#!/usr/bin/env python3
"""Were the samplers running during each run?  Compares sampler files with each run's metadata.txt times.
usage (repo root): python monitoring/check_coverage.py web="mon_web_*.csv" db="mon_db_*.csv" load="mon_load_*.csv" [--results results]
Prints, per run, the % of its seconds (start_utc..end_utc) that have a sample from each VM. Aim for >= 90%."""
import glob, sys
from pathlib import Path
import pandas as pd

args = sys.argv[1:]
res = Path(args[args.index("--results") + 1]) if "--results" in args else Path("results")
srcs = dict(a.split("=", 1) for a in args if "=" in a and not a.startswith("--"))
if not srcs: sys.exit(__doc__)
data = {}
for role, pat in srcs.items():
    files = [f for p in pat.split(",") for f in sorted(glob.glob(p))]
    if not files: print(f"{role}: NO FILES match {pat}"); continue
    df = pd.concat([pd.read_csv(f) for f in files]).sort_values("ts_epoch"); data[role] = df
    print(f"{role}: {len(files)} file(s), {len(df)} rows, {pd.to_datetime(df.ts_epoch.min(), unit='s', utc=True):%Y-%m-%d %H:%M:%S} -> {pd.to_datetime(df.ts_epoch.max(), unit='s', utc=True):%Y-%m-%d %H:%M:%S} UTC")
print()
bad = 0
for d in sorted(p for p in res.iterdir() if (p / "metadata.txt").exists()):
    m = dict(l.split("=", 1) for l in (d / "metadata.txt").read_text().splitlines() if "=" in l)
    t0, t1 = pd.Timestamp(m["start_utc"]).timestamp(), pd.Timestamp(m["end_utc"]).timestamp()
    cells = []
    for role, df in data.items():
        pct = 100 * ((df.ts_epoch >= t0) & (df.ts_epoch <= t1)).sum() / max(t1 - t0, 1)
        cells.append(f"{role} {pct:5.0f}%"); bad += pct < 90
    print(f"{m['run_id']:<26} {m['start_utc']}  " + "   ".join(cells))
print(f"\n{bad} run/VM combination(s) below 90% coverage" + ("  -> those runs need repeating." if bad else "  -> samplers covered the runs."))
