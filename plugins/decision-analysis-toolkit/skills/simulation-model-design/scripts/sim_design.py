#!/usr/bin/env python3
"""Size a Monte Carlo run, solve a newsvendor order, and show the flaw of averages.

  python3 sim_design.py --runs --pilot-std 1200 --half-width 100
  python3 sim_design.py --runs --pilot-p 0.15 --half-width 0.01
  python3 sim_design.py --newsvendor --price 12 --cost 5 --salvage 1 \
      --demand-mean 1000 --demand-sd 300 [--demand-csv history.csv --demand-col units]
  python3 sim_design.py --selftest
Needs numpy.
"""
import argparse
import math
import sys
from statistics import NormalDist

try:
    import numpy as np
except ImportError:
    sys.exit("needs numpy: pip install numpy")


def runs_for_mean(std, half_width, conf=0.95):
    z = NormalDist().inv_cdf(0.5 + conf / 2)
    return math.ceil((z * std / half_width) ** 2)


def runs_for_probability(p, half_width, conf=0.95):
    z = NormalDist().inv_cdf(0.5 + conf / 2)
    return math.ceil(z * z * p * (1 - p) / half_width ** 2)


def newsvendor(demand, price, cost, salvage=0.0, candidates=None):
    """demand: array of simulated or historical demand. Returns critical ratio, best q, table."""
    under, over = price - cost, cost - salvage
    ratio = under / (under + over)
    q_star = float(np.quantile(demand, ratio))
    candidates = np.unique(np.round(np.quantile(demand, np.linspace(0.05, 0.95, 19)))) if candidates is None else candidates
    rows = []
    for q in list(candidates) + [round(q_star)]:
        sold = np.minimum(demand, q)
        profit = price * sold + salvage * (q - sold) - cost * q
        rows.append((q, profit.mean(), profit.std(), (demand <= q).mean(), sold.sum() / demand.sum()))
    rows.sort()
    return ratio, q_star, rows


def selftest():
    rng = np.random.default_rng(7)
    assert runs_for_mean(1200, 100) == 554
    assert runs_for_probability(0.15, 0.01) == 4898

    # flaw of averages 1: two parallel tasks, each 10 days on average
    a, b = rng.triangular(6, 10, 14, 100_000), rng.triangular(6, 10, 14, 100_000)
    assert np.maximum(a, b).mean() > 10.8, "a project waiting on parallel tasks runs later than its average-input plan"

    # flaw of averages 2: sales capped by stock
    demand = rng.normal(1000, 300, 100_000).clip(0)
    assert np.minimum(demand, 1000).mean() < 900, "stocking the mean sells well below the mean"

    ratio, q, rows = newsvendor(demand, price=12, cost=5, salvage=1)
    assert abs(ratio - 7 / 11) < 1e-9 and q > 1000, "cheap overage and costly underage mean order above mean demand"
    best_q = max(rows, key=lambda r: r[1])[0]
    assert abs(best_q - q) < 80, "the critical-ratio quantity is near the simulated profit maximum"
    ratio2, q2, _ = newsvendor(demand, price=6, cost=5, salvage=0)
    assert q2 < 1000, "thin margins with no salvage mean order below mean demand"
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", action="store_true")
    ap.add_argument("--pilot-std", type=float)
    ap.add_argument("--pilot-p", type=float)
    ap.add_argument("--half-width", type=float)
    ap.add_argument("--conf", type=float, default=0.95)
    ap.add_argument("--newsvendor", action="store_true")
    ap.add_argument("--price", type=float)
    ap.add_argument("--cost", type=float)
    ap.add_argument("--salvage", type=float, default=0.0)
    ap.add_argument("--demand-mean", type=float)
    ap.add_argument("--demand-sd", type=float)
    ap.add_argument("--demand-csv")
    ap.add_argument("--demand-col")
    ap.add_argument("--n", type=int, default=100_000)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.runs:
        if a.half_width is None or (a.pilot_std is None) == (a.pilot_p is None):
            ap.error("--runs needs --half-width and one of --pilot-std or --pilot-p")
        n = runs_for_mean(a.pilot_std, a.half_width, a.conf) if a.pilot_std is not None \
            else runs_for_probability(a.pilot_p, a.half_width, a.conf)
        print(f"runs needed for ±{a.half_width:g} at {a.conf:.0%} confidence: {n:,}")
        return
    if a.newsvendor:
        if a.price is None or a.cost is None:
            ap.error("--newsvendor needs --price and --cost")
        if a.demand_csv:
            import csv
            with open(a.demand_csv) as fh:
                demand = np.array([float(r[a.demand_col]) for r in csv.DictReader(fh)])
        elif a.demand_mean is not None and a.demand_sd is not None:
            demand = np.random.default_rng(a.seed).normal(a.demand_mean, a.demand_sd, a.n).clip(0)
        else:
            ap.error("give --demand-csv and --demand-col, or --demand-mean and --demand-sd")
        ratio, q, rows = newsvendor(demand, a.price, a.cost, a.salvage)
        print(f"critical ratio {ratio:.3f}: order about {q:,.0f} (mean demand {demand.mean():,.0f})\n")
        print(f"{'order':>8} {'mean profit':>12} {'profit sd':>10} {'P(no stockout)':>15} {'fill rate':>10}")
        for q_, m, s, cs, fr in rows:
            print(f"{q_:>8,.0f} {m:>12,.0f} {s:>10,.0f} {cs:>15.2f} {fr:>10.3f}")
        return
    ap.error("choose --runs, --newsvendor or --selftest")


if __name__ == "__main__":
    main()
