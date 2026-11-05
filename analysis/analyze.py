#!/usr/bin/env python3
"""Aggregate k6 + monitoring data and make figures/tables.
usage (repo root): python analysis/analyze.py [results_dir=results] [matrix=load-tests/run_matrix.csv]
needs: pandas numpy matplotlib

Per run (results/<run_id>/): metadata.txt, raw.json.gz, summary.json, <run_id>_{web,db,load}.csv
Only k6 points tagged phase=measure are used; the monitoring window is the first..last such point.
"""
import gzip, json, re, sys
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

RES = Path(sys.argv[1] if len(sys.argv) > 1 else "results")
MATRIX = Path(sys.argv[2] if len(sys.argv) > 2 else "load-tests/run_matrix.csv")
OUT = Path("analysis/output"); OUT.mkdir(parents=True, exist_ok=True)
ROLES = ("web", "db", "load")
HOT_CPU = 80.0          # flag db/load VM if p95 of 1-s CPU samples exceeds this (%)
KEEP = {"http_req_duration", "http_reqs", "http_req_failed", "app_check_failed"}

def secs(s):
    m = re.fullmatch(r"(\d+)([smh])", s.strip())
    return int(m[1]) * {"s": 1, "m": 60, "h": 3600}[m[2]] if m else None

def read_meta(p):
    d = {}
    for line in p.read_text().splitlines():
        if "=" in line:
            k, v = line.split("=", 1); d[k.strip()] = v.strip()
    return d

def load_k6(path):
    dur, failed, app, times, nreq = [], [], [], [], 0
    with gzip.open(path, "rt") as f:
        for line in f:
            if '"Point"' not in line: continue
            o = json.loads(line)
            m = o.get("metric")
            if m not in KEEP: continue
            d = o["data"]
            if d.get("tags", {}).get("phase") != "measure": continue
            times.append(d["time"])
            if m == "http_req_duration": dur.append(d["value"])
            elif m == "http_reqs": nreq += d["value"]
            elif m == "http_req_failed": failed.append(d["value"])
            elif m == "app_check_failed": app.append(d["value"])
    if not times: return None
    t = pd.to_datetime(pd.Series(times), utc=True, format="ISO8601")
    return dict(dur=np.array(dur), nreq=int(nreq), http_fail=float(np.sum(failed)), app_fail=float(np.sum(app)),
                t0=t.min().timestamp(), t1=t.max().timestamp())

def mon_stats(path, t0, t1, role, nominal_s):
    if not path.exists(): return {}
    d = pd.read_csv(path)
    d = d[(d.ts_epoch >= t0) & (d.ts_epoch <= t1)]
    if d.empty: return {f"{role}_samples": 0}
    return {f"{role}_samples": len(d), f"{role}_coverage": len(d) / nominal_s,
            f"{role}_cpu_mean": d.cpu_pct.mean(), f"{role}_cpu_p95": d.cpu_pct.quantile(.95), f"{role}_cpu_max": d.cpu_pct.max(),
            f"{role}_mem_mean_mb": d.mem_used_mb.mean(), f"{role}_mem_max_mb": d.mem_used_mb.max(),
            f"{role}_mem_mean_pct": d.mem_used_pct.mean()}

rows, status = [], []
matrix = pd.read_csv(MATRIX) if MATRIX.exists() else None
for d in sorted(p for p in RES.iterdir() if p.is_dir()):
    mp, rp = d / "metadata.txt", d / "raw.json.gz"
    if not (mp.exists() and rp.exists()):
        status.append(dict(run_id=d.name, issue="missing metadata.txt or raw.json.gz")); continue
    m = read_meta(mp); k = load_k6(rp)
    if k is None:
        status.append(dict(run_id=d.name, issue="no measure-phase points in raw data")); continue
    nominal = secs(m.get("duration", "")) or (k["t1"] - k["t0"])
    n = k["nreq"]
    r = dict(run_id=m["run_id"], deployment=m["deployment"], users=int(m["users"]), rep=int(m["repetition"]),
             workload=m.get("workload", "unknown"), k6_exit=int(m.get("k6_exit_code", -1)),
             requests=n, p95_ms=float(np.percentile(k["dur"], 95)), median_ms=float(np.median(k["dur"])),
             http_fail_pct=100 * k["http_fail"] / n, app_fail_pct=100 * k["app_fail"] / n,
             ok_rps=(n - k["http_fail"] - k["app_fail"]) / nominal, window_s=k["t1"] - k["t0"], nominal_s=nominal)
    for role in ROLES:
        r.update(mon_stats(d / f"{m['run_id']}_{role}.csv", k["t0"], k["t1"], role, nominal))
    rows.append(r)
    if r["k6_exit"] != 0: status.append(dict(run_id=r["run_id"], issue=f"k6 exit code {r['k6_exit']} (threshold breach or error); data kept"))
    if abs(r["window_s"] - nominal) / nominal > 0.05: status.append(dict(run_id=r["run_id"], issue=f"measure window {r['window_s']:.0f}s vs nominal {nominal}s"))
    for role in ROLES:
        if r.get(f"{role}_coverage", 0) < 0.9: status.append(dict(run_id=r["run_id"], issue=f"{role} monitoring coverage {r.get(f'{role}_coverage', 0):.0%} (<90%)"))
    for role in ("db", "load"):
        if r.get(f"{role}_cpu_p95", 0) > HOT_CPU: status.append(dict(run_id=r["run_id"], issue=f"{role} VM CPU p95 {r[f'{role}_cpu_p95']:.0f}% > {HOT_CPU:.0f}% (possible bottleneck)"))
if matrix is not None:
    done = {r["run_id"] for r in rows}
    for rid in matrix.run_id:
        if rid not in done: status.append(dict(run_id=rid, issue="in run_matrix.csv but no usable results"))
runs = pd.DataFrame(rows).sort_values(["workload", "deployment", "users", "rep"])
runs.to_csv(OUT / "runs.csv", index=False)
pd.DataFrame(status, columns=["run_id", "issue"]).to_csv(OUT / "run_status.csv", index=False)

def agg(df):
    g = df.groupby(["workload", "deployment", "users"])
    a = g.agg(n=("rep", "count"),
              p95_mean=("p95_ms", "mean"), p95_sd=("p95_ms", "std"), p95_min=("p95_ms", "min"), p95_max=("p95_ms", "max"),
              rps_mean=("ok_rps", "mean"), rps_sd=("ok_rps", "std"),
              web_cpu_mean=("web_cpu_mean", "mean"), web_cpu_sd=("web_cpu_mean", "std"),
              web_mem_mb=("web_mem_mean_mb", "mean"), web_mem_sd=("web_mem_mean_mb", "std"),
              http_fail_pct=("http_fail_pct", "mean"), app_fail_pct=("app_fail_pct", "mean"),
              db_cpu_p95_max=("db_cpu_p95", "max"), load_cpu_p95_max=("load_cpu_p95", "max"))
    return a.reset_index()
summ = agg(runs); summ.to_csv(OUT / "summary_table.csv", index=False)

def md(df, cols, fmt):
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for _, r in df.iterrows():
        lines.append("| " + " | ".join(fmt.get(c, "{}").format(r[c]) for c in cols) + " |")
    return "\n".join(lines)
tbl = summ[["workload", "deployment", "users", "n", "http_fail_pct", "app_fail_pct", "web_mem_mb", "web_mem_sd"]]
(OUT / "error_memory_table.md").write_text(md(tbl, list(tbl.columns),
    {"http_fail_pct": "{:.2f}", "app_fail_pct": "{:.2f}", "web_mem_mb": "{:.0f}", "web_mem_sd": "{:.0f}"}) + "\n")

def plot(wl, col, ylabel, fname):
    sub = runs[runs.workload == wl]
    fig, ax = plt.subplots(figsize=(6, 4))
    deps = sorted(sub.deployment.unique())
    for i, dep in enumerate(deps):
        g = sub[sub.deployment == dep]; off = (i - (len(deps) - 1) / 2) * 1.2
        ax.scatter(g.users + off, g[col], s=14, alpha=.35)
        s = g.groupby("users")[col].agg(["mean", "std"])
        ax.errorbar(s.index + off, s["mean"], yerr=s["std"].fillna(0), marker="o", capsize=3, label=f"{dep} (n={g.groupby('users').size().min()}-{g.groupby('users').size().max()})")
    ax.set_xticks(sorted(sub.users.unique())); ax.set_xlabel("Concurrent users (k6 VUs)"); ax.set_ylabel(ylabel)
    ax.set_title(f"{wl}\nmean ± SD across repetitions; dots = individual runs", fontsize=9)
    ax.grid(alpha=.3); ax.legend(); fig.tight_layout(); fig.savefig(OUT / fname, dpi=200); plt.close(fig)

for wl in runs.workload.unique():
    sfx = re.sub(r"[^a-z0-9]+", "-", wl.lower())
    plot(wl, "p95_ms", "p95 response time (ms)", f"p95_vs_users_{sfx}.png")
    plot(wl, "ok_rps", "Successful requests/s", f"rps_vs_users_{sfx}.png")
    plot(wl, "web_cpu_mean", "Web VM CPU, mean over measure phase (%)", f"webcpu_vs_users_{sfx}.png")

pd.set_option("display.width", 200)
print(summ.round(2).to_string(index=False))
print("\nRun status / issues:"); print(pd.DataFrame(status, columns=["run_id", "issue"]).to_string(index=False) if status else "none")
