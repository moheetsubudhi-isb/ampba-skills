#!/usr/bin/env python3
"""Plan and read a two-arm randomised experiment (A/B test).

  python3 ab_test_plan.py plan --baseline 0.10 --lift 0.01 --daily 4000
  python3 ab_test_plan.py plan --sd 12 --effect 0.5            # continuous metric
  python3 ab_test_plan.py mde --baseline 0.10 --n 20000         # smallest lift detectable
  python3 ab_test_plan.py read --a-n 10000 --a-x 1000 --b-n 10050 --b-x 1130
  python3 ab_test_plan.py --selftest

plan: sample size per arm, and days needed if --daily (visitors per day, both arms).
mde:  smallest absolute lift a given per-arm sample can detect at the stated power.
read: difference, confidence interval, p-value and a sample-ratio check for a
      conversion-style metric. --planned-share is the intended share in arm B.
Standard library; numpy is needed only for --selftest.
"""
import argparse
import math
import sys
from statistics import NormalDist

N = NormalDist()


def n_prop(p1, p2, alpha=0.05, power=0.8):
    za, zb = N.inv_cdf(1 - alpha / 2), N.inv_cdf(power)
    pbar = (p1 + p2) / 2
    num = za * math.sqrt(2 * pbar * (1 - pbar)) + zb * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))
    return num ** 2 / (p2 - p1) ** 2


def n_mean(sd, effect, alpha=0.05, power=0.8):
    za, zb = N.inv_cdf(1 - alpha / 2), N.inv_cdf(power)
    return 2 * ((za + zb) * sd / effect) ** 2


def mde_prop(p1, n, alpha=0.05, power=0.8):
    lo, hi = 1e-9, 1 - p1 - 1e-9
    for _ in range(80):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if n_prop(p1, p1 + mid, alpha, power) > n else (lo, mid)
    return (lo + hi) / 2


def read_prop(a_n, a_x, b_n, b_x, planned_share=0.5):
    pa, pb = a_x / a_n, b_x / b_n
    diff = pb - pa
    se = math.sqrt(pa * (1 - pa) / a_n + pb * (1 - pb) / b_n)
    pool = (a_x + b_x) / (a_n + b_n)
    se0 = math.sqrt(pool * (1 - pool) * (1 / a_n + 1 / b_n))
    z = diff / se0
    total = a_n + b_n
    srm_z = (b_n - planned_share * total) / math.sqrt(total * planned_share * (1 - planned_share))
    return {"rate_a": pa, "rate_b": pb, "diff": diff, "rel_lift": diff / pa if pa else float("nan"),
            "ci": (diff - 1.96 * se, diff + 1.96 * se), "p": 2 * (1 - N.cdf(abs(z))),
            "srm_p": 2 * (1 - N.cdf(abs(srm_z)))}


def selftest():
    try:
        import numpy as np
    except ImportError:
        sys.exit("needs numpy for the selftest: pip install numpy")
    n = n_prop(0.10, 0.11)
    assert 14700 < n < 14800, n
    assert 3.7 < n_prop(0.10, 0.105) / n < 4.3, "halving the lift needs about four times the sample"
    assert abs(mde_prop(0.10, n) - 0.01) < 5e-4, "mde inverts the sample-size formula"
    assert n_mean(12, 0.5) > 4 * n_mean(12, 1.0) * 0.99, "a smaller effect on a noisy metric needs far more users"

    rng = np.random.default_rng(3)
    k, m, reps = 10, 1000, 4000
    a = rng.binomial(m, 0.1, (reps, k)).cumsum(1)
    b = rng.binomial(m, 0.1, (reps, k)).cumsum(1)
    cum_n = m * np.arange(1, k + 1)
    pool = (a + b) / (2 * cum_n)
    z = (b - a) / cum_n / np.sqrt(pool * (1 - pool) * 2 / cum_n)
    hit_any = (np.abs(z) > 1.96).any(1).mean()
    hit_last = (np.abs(z[:, -1]) > 1.96).mean()
    assert hit_last < 0.08 and hit_any > 0.15, (hit_last, hit_any)  # peeking inflates false wins

    assert read_prop(10000, 1000, 10050, 1130)["p"] < 0.01
    assert read_prop(5200, 500, 4800, 480)["srm_p"] < 0.001, "a 52/48 split of 10,000 is a broken assignment"
    assert read_prop(5020, 500, 4980, 500)["srm_p"] > 0.05
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--selftest", action="store_true")
    sub = ap.add_subparsers(dest="cmd")
    for name in ("plan", "mde", "read"):
        sp = sub.add_parser(name)
        if name in ("plan", "mde"):
            sp.add_argument("--alpha", type=float, default=0.05)
            sp.add_argument("--power", type=float, default=0.8)
        if name == "plan":
            sp.add_argument("--baseline", type=float)
            sp.add_argument("--lift", type=float, help="absolute lift, e.g. 0.01 for one point")
            sp.add_argument("--sd", type=float)
            sp.add_argument("--effect", type=float)
            sp.add_argument("--daily", type=float)
        if name == "mde":
            sp.add_argument("--baseline", type=float, required=True)
            sp.add_argument("--n", type=float, required=True, help="users per arm")
        if name == "read":
            for f in ("a-n", "a-x", "b-n", "b-x"):
                sp.add_argument("--" + f, type=float, required=True)
            sp.add_argument("--planned-share", type=float, default=0.5)
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.cmd == "plan":
        if a.baseline is not None and a.lift is not None:
            n = n_prop(a.baseline, a.baseline + a.lift, a.alpha, a.power)
        elif a.sd is not None and a.effect is not None:
            n = n_mean(a.sd, a.effect, a.alpha, a.power)
        else:
            ap.error("plan needs --baseline and --lift, or --sd and --effect")
        print(f"{math.ceil(n):,} per arm, {2 * math.ceil(n):,} in total (alpha {a.alpha}, power {a.power})")
        if a.daily:
            days = math.ceil(2 * n / a.daily)
            print(f"{days} days at {a.daily:,.0f} visitors a day; run whole weeks: {math.ceil(days / 7) * 7} days")
    elif a.cmd == "mde":
        print(f"smallest detectable absolute lift: {mde_prop(a.baseline, a.n, a.alpha, a.power):.4f} "
              f"({mde_prop(a.baseline, a.n, a.alpha, a.power) / a.baseline:.1%} relative)")
    elif a.cmd == "read":
        r = read_prop(a.a_n, a.a_x, a.b_n, a.b_x, a.planned_share)
        print(f"A {r['rate_a']:.4f}   B {r['rate_b']:.4f}   difference {r['diff']:+.4f} ({r['rel_lift']:+.1%} relative)")
        print(f"95% CI for the difference: {r['ci'][0]:+.4f} to {r['ci'][1]:+.4f}   p = {r['p']:.4f}")
        if r["srm_p"] < 0.001:
            print(f"WARNING: sample ratio mismatch (p = {r['srm_p']:.2g}). Assignment is broken; do not trust this result.")
        else:
            print(f"sample ratio check passed (p = {r['srm_p']:.2f})")
    else:
        ap.error("choose plan, mde, read or --selftest")


if __name__ == "__main__":
    main()
