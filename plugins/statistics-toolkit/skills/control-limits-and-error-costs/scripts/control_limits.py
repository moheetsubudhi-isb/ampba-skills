#!/usr/bin/env python3
"""Set control limits and thresholds for a monitored measurement, from error costs.

  python3 control_limits.py limits --mean 500 --sd 8 --n 4 [--k 3]
  python3 control_limits.py detect --mean 500 --sd 8 --n 4 --shift 6 [--k 3]
  python3 control_limits.py alpha --sd 8 --n 4 --shift 6 --cost-false-alarm 200 --cost-miss 5000 --prior-shift 0.05
  python3 control_limits.py spec --mean 505 --sd 8 --lsl 490 [--usl 530]
  python3 control_limits.py spec --sd 8 --lsl 490 --max-breach 0.01     # target average needed
  python3 control_limits.py --selftest

limits: limits for the average of n readings, false-alarm rate per check and the
        average run length between false alarms.
detect: chance one check catches a shift of the stated size, and how many checks
        it takes on average.
alpha:  the false-alarm rate that minimises expected cost per check, given what a
        false alarm costs, what a miss costs and how often the process really shifts.
spec:   chance of breaching a spec limit, or the average needed to keep breaches
        below a target rate. Assumes roughly normal readings.
Standard library only.
"""
import argparse
import math
import sys
from statistics import NormalDist

N = NormalDist()


def limits(mean, sd, n, k=3.0):
    se = sd / math.sqrt(n)
    far = 2 * (1 - N.cdf(k))
    return mean - k * se, mean + k * se, far, 1 / far


def power(sd, n, shift, k=3.0):
    delta = shift / (sd / math.sqrt(n))
    beta = N.cdf(k - delta) - N.cdf(-k - delta)
    return 1 - beta


def best_alpha(sd, n, shift, cost_fa, cost_miss, prior_shift):
    best = None
    for i in range(1, 2000):
        alpha = i / 2000 * 0.5
        k = N.inv_cdf(1 - alpha / 2)
        cost = (1 - prior_shift) * alpha * cost_fa + prior_shift * (1 - power(sd, n, shift, k)) * cost_miss
        if best is None or cost < best[0]:
            best = (cost, alpha, k)
    return best[1], best[2], best[0]


def breach(mean, sd, lsl=None, usl=None):
    lo = N.cdf((lsl - mean) / sd) if lsl is not None else 0.0
    hi = 1 - N.cdf((usl - mean) / sd) if usl is not None else 0.0
    return lo, hi


def selftest():
    lo, hi, far, arl = limits(500, 8, 4)
    assert abs(far - 0.0027) < 1e-4 and abs(arl - 370.4) < 1, "3-sigma limits: 1 false alarm in about 370 checks"
    assert abs(lo - 488) < 1e-9 and abs(hi - 512) < 1e-9, "averages of 4 readings get limits half as wide"
    p1 = power(8, 1, 8)
    assert abs(1 / p1 - 43.9) < 0.5, "a 1-sigma shift takes about 44 single readings to catch"
    assert abs(1 / power(8, 4, 8) - 6.3) < 0.2, "averaging 4 readings cuts that to about 6 checks"
    a_low, _, _ = best_alpha(8, 4, 6, 200, 500, 0.05)
    a_high, _, _ = best_alpha(8, 4, 6, 200, 50000, 0.05)
    assert a_high > a_low, "when a miss costs far more than a false alarm, tighten the limits (higher alpha)"
    k = N.inv_cdf(0.99)
    need = 490 + k * 8
    assert abs(breach(need, 8, lsl=490)[0] - 0.01) < 1e-9 and abs(need - 508.6) < 0.1
    assert breach(490, 8, lsl=490)[0] == 0.5, "centring the process on the limit breaches half the time"
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--selftest", action="store_true")
    sub = ap.add_subparsers(dest="cmd")
    for name in ("limits", "detect"):
        sp = sub.add_parser(name)
        sp.add_argument("--mean", type=float, required=True)
        sp.add_argument("--sd", type=float, required=True)
        sp.add_argument("--n", type=int, default=1)
        sp.add_argument("--k", type=float, default=3.0, help="limit width in standard errors")
        if name == "detect":
            sp.add_argument("--shift", type=float, required=True, help="size of the shift, in measurement units")
    al = sub.add_parser("alpha")
    al.add_argument("--sd", type=float, required=True)
    al.add_argument("--n", type=int, default=1)
    al.add_argument("--shift", type=float, required=True)
    al.add_argument("--cost-false-alarm", type=float, required=True)
    al.add_argument("--cost-miss", type=float, required=True)
    al.add_argument("--prior-shift", type=float, required=True, help="share of checks where the process has really shifted")
    sp = sub.add_parser("spec")
    sp.add_argument("--mean", type=float)
    sp.add_argument("--sd", type=float, required=True)
    sp.add_argument("--lsl", type=float)
    sp.add_argument("--usl", type=float)
    sp.add_argument("--max-breach", type=float)
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.cmd == "limits":
        lo, hi, far, arl = limits(a.mean, a.sd, a.n, a.k)
        print(f"limits for the average of {a.n}: {lo:.4g} to {hi:.4g}")
        print(f"false alarm rate per check {far:.4f}; about one false alarm every {arl:,.0f} checks")
    elif a.cmd == "detect":
        pw = power(a.sd, a.n, a.shift, a.k)
        print(f"chance one check catches a shift of {a.shift:g}: {pw:.1%}; on average {1 / pw:.1f} checks to catch it")
    elif a.cmd == "alpha":
        alpha, k, cost = best_alpha(a.sd, a.n, a.shift, a.cost_false_alarm, a.cost_miss, a.prior_shift)
        print(f"cheapest false alarm rate {alpha:.4f} (limits at {k:.2f} standard errors), expected cost {cost:,.2f} per check")
        print(f"at that setting a real shift of {a.shift:g} is caught {power(a.sd, a.n, a.shift, k):.1%} of the time per check")
    elif a.cmd == "spec":
        if a.max_breach is not None:
            if a.lsl is None and a.usl is None:
                ap.error("give --lsl or --usl with --max-breach")
            z = N.inv_cdf(1 - a.max_breach)
            if a.lsl is not None:
                print(f"average needed to keep breaches of the lower limit below {a.max_breach:.2%}: {a.lsl + z * a.sd:.4g}")
            if a.usl is not None:
                print(f"average needed to keep breaches of the upper limit below {a.max_breach:.2%}: {a.usl - z * a.sd:.4g}")
        else:
            if a.mean is None:
                ap.error("spec needs --mean, or --max-breach to solve for the average")
            lo, hi = breach(a.mean, a.sd, a.lsl, a.usl)
            print(f"chance of a reading below the lower limit {lo:.2%}; above the upper limit {hi:.2%}; total {lo + hi:.2%}")
    else:
        ap.error("choose limits, detect, alpha, spec or --selftest")


if __name__ == "__main__":
    main()
