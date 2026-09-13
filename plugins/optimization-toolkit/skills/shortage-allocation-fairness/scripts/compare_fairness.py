#!/usr/bin/env python3
"""Show how different allocation rules split the same scarce supply.

Brute force over whole-unit plans, so keep the problem small (a few claimants,
demands in the tens). Reports each rule's chosen plan, how many plans tie, the
range of total shortfall across those ties, and the price of fairness: value
served by the most efficient plan minus value served by the rule's plan.

  python3 compare_fairness.py --demand 20 5 5 --supply 20 --value 3 1 1
  python3 compare_fairness.py --selftest
"""
import argparse
import itertools
import math
import sys

MAX_PLANS = 2_000_000


def plans(demand, supply):
    for served in itertools.product(*(range(d + 1) for d in demand)):
        if sum(served) <= supply:
            yield served


def metrics(served, demand, value):
    short = [d - s for d, s in zip(demand, served)]
    pct = [s / d if d else 0.0 for s, d in zip(short, demand)]
    r = lambda v: round(v, 9)  # stable ties for fractional scores
    return {
        "neg_value": -sum(s * v for s, v in zip(served, value)),
        "total": sum(short),
        "worst_units": max(short),
        "worst_pct": r(max(pct)),
        "sq_units": sum(s * s for s in short),
        "sq_pct": r(sum(p * p for p in pct)),
    }


RULES = {
    "Efficiency: most value served": ("neg_value", "total"),
    "Protect worst-off (units)": ("worst_units",),
    "Protect worst-off (% of need)": ("worst_pct",),
    "Spread pain (squared units)": ("sq_units",),
    "Spread pain (squared % of need)": ("sq_pct",),
    "Two-stage: worst-off %, then value": ("worst_pct", "neg_value"),
}


def solve(demand, supply, value=None):
    value = value or [1] * len(demand)
    if math.prod(d + 1 for d in demand) > MAX_PLANS:
        raise SystemExit("too many plans to enumerate; shrink demands or claimants")
    scored = [(p, metrics(p, demand, value)) for p in plans(demand, supply)]
    out = {}
    for rule, keys in RULES.items():
        best = min(tuple(m[k] for k in keys) for _, m in scored)
        ties = [(p, m) for p, m in scored if tuple(m[k] for k in keys) == best]
        out[rule] = ties
    return out


def report(demand, supply, value):
    results = solve(demand, supply, value)
    best_value = -results[next(iter(RULES))][0][1]["neg_value"]
    print(f"Demand {demand} (total {sum(demand)}), supply {supply}, value per unit {value}\n")
    for rule, ties in results.items():
        plan, m = min(ties, key=lambda t: (t[1]["neg_value"], t[1]["total"], t[0]))
        totals = [t[1]["total"] for t in ties]
        met = [f"{s / d:.0%}" if d else "-" for s, d in zip(plan, demand)]
        print(f"{rule}\n  example plan {plan}  need met {met}  total short {m['total']}"
              f"  value {-m['neg_value']}  price of fairness {best_value + m['neg_value']}"
              f"\n  tied plans {len(ties)}  (total short across ties {min(totals)}..{max(totals)})")


def selftest():
    r = solve([10, 10], 10)
    eff = [p for p, _ in r["Efficiency: most value served"]]
    assert len(eff) > 1 and (10, 0) in eff and (5, 5) in eff, "efficiency ties hide unfair plans"
    assert [p for p, _ in r["Protect worst-off (units)"]] == [(5, 5)], "min-max splits evenly"
    assert [p for p, _ in r["Spread pain (squared units)"]] == [(5, 5)], "squared penalty splits evenly"
    r = solve([20, 5, 5], 20)
    mm = [m["total"] for _, m in r["Protect worst-off (units)"]]
    assert len(mm) > 1 and max(mm) > min(mm), "min-max alone ties with plans that waste supply"
    best_total = min(m["total"] for _, m in r["Efficiency: most value served"])
    assert all(m["total"] == best_total for _, m in r["Two-stage: worst-off %, then value"]), "two-stage wastes nothing"
    r = solve([10, 10], 10, [3, 1])
    assert [p for p, _ in r["Efficiency: most value served"]] == [(10, 0)], "efficiency serves the valuable claimant"
    fair = r["Protect worst-off (units)"]
    assert [p for p, _ in fair] == [(5, 5)] and -fair[0][1]["neg_value"] == 20, "fairness costs 30 - 20 = 10"
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--demand", nargs="+", type=int)
    ap.add_argument("--supply", type=int)
    ap.add_argument("--value", nargs="+", type=float, help="value per unit served, one per claimant (default 1)")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.demand or a.supply is None or a.supply < 0 or min(a.demand) < 0:
        ap.error("give --demand (non-negative integers) and --supply")
    if a.value and len(a.value) != len(a.demand):
        ap.error("--value needs one number per claimant")
    report(a.demand, a.supply, a.value or [1] * len(a.demand))


if __name__ == "__main__":
    main()
