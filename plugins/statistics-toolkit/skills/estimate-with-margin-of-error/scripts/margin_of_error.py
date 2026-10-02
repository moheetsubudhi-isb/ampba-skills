#!/usr/bin/env python3
"""Estimate an average or a rate from a sample with a margin of error, or size a sample.

  python3 margin_of_error.py mean --mean 42.5 --sd 11 --n 36
  python3 margin_of_error.py mean --csv audit.csv --col days_to_close
  python3 margin_of_error.py prop --x 7 --n 120
  python3 margin_of_error.py size --kind mean --sd 11 --margin 2 [--population 5000]
  python3 margin_of_error.py size --kind prop --p 0.5 --margin 0.03 [--population 5000]
  python3 margin_of_error.py --selftest

mean: t interval (right for small samples; close to z for large ones).
prop: Wilson interval (reliable for small counts and rates near 0 or 1) next to
      the textbook Wald interval, so the gap is visible.
size: sample needed for a target half-width; --population applies the
      finite-population correction. Use --p 0.5 when the rate is unknown.
Standard library; numpy is needed only for --csv and --selftest.
"""
import argparse
import math
import sys
from statistics import NormalDist

N = NormalDist()

def _betacf(a, b, x):
    tiny, qab, qap, qam = 1e-300, a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > tiny else tiny)
    h = d
    for m in range(1, 300):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-12:
            break
    return h


def betainc(a, b, x):
    """Regularised incomplete beta I_x(a, b)."""
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    front = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log1p(-x))
    if x < (a + 1) / (a + b + 2):
        return front * _betacf(a, b, x) / a
    return 1 - front * _betacf(b, a, 1 - x) / b


def t_sf(t, df):
    """P(T > t) for Student t with df degrees of freedom."""
    p = 0.5 * betainc(df / 2, 0.5, df / (df + t * t))
    return p if t > 0 else 1 - p


def t_ppf(p, df):
    """Quantile of Student t (bisection)."""
    lo, hi = -1e3, 1e3
    for _ in range(200):
        mid = (lo + hi) / 2
        if 1 - t_sf(mid, df) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2




def t_interval(mean, sd, n, conf=0.95):
    c = t_ppf(0.5 + conf / 2, n - 1)
    half = c * sd / math.sqrt(n)
    return mean - half, mean + half, half


def wilson(x, n, conf=0.95):
    z = N.inv_cdf(0.5 + conf / 2)
    p = x / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return centre - half, centre + half


def wald(x, n, conf=0.95):
    z = N.inv_cdf(0.5 + conf / 2)
    p = x / n
    half = z * math.sqrt(p * (1 - p) / n)
    return p - half, p + half


def size_mean(sd, margin, conf=0.95, population=None):
    z = N.inv_cdf(0.5 + conf / 2)
    n = (z * sd / margin) ** 2
    return n / (1 + (n - 1) / population) if population else n


def size_prop(p, margin, conf=0.95, population=None):
    z = N.inv_cdf(0.5 + conf / 2)
    n = z * z * p * (1 - p) / margin ** 2
    return n / (1 + (n - 1) / population) if population else n


def exact_coverage(interval, p, n):
    cover = 0.0
    for x in range(n + 1):
        lo, hi = interval(x, n)
        if lo <= p <= hi:
            cover += math.comb(n, x) * p ** x * (1 - p) ** (n - x)
    return cover


def selftest():
    try:
        import numpy as np
    except ImportError:
        sys.exit("needs numpy for the selftest: pip install numpy")
    rng = np.random.default_rng(11)
    hits = 0
    for _ in range(5000):
        s = rng.normal(10, 3, 10)
        lo, hi, _h = t_interval(s.mean(), s.std(ddof=1), 10)
        hits += lo <= 10 <= hi
    assert 0.94 < hits / 5000 < 0.96, "a 95% t interval covers the truth about 95% of the time"
    assert t_ppf(0.975, 9) > 1.96, "small samples need a wider multiplier than 1.96"
    assert exact_coverage(wald, 0.02, 50) < 0.80, "the textbook interval fails for rare events"
    assert exact_coverage(wilson, 0.02, 50) > 0.90
    assert 3.9 < size_mean(11, 1) / size_mean(11, 2) < 4.1, "halving the margin quadruples the sample"
    assert size_prop(0.5, 0.03, population=1000) < 0.6 * size_prop(0.5, 0.03), "a small population needs fewer records"
    assert round(size_prop(0.5, 0.03)) == 1067
    lo, hi = wilson(0, 40)
    assert abs(lo) < 1e-9 and 0.05 < hi < 0.12, "zero events in 40 still leaves room for a rate near 9%"
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--selftest", action="store_true")
    sub = ap.add_subparsers(dest="cmd")
    m = sub.add_parser("mean")
    m.add_argument("--mean", type=float)
    m.add_argument("--sd", type=float)
    m.add_argument("--n", type=int)
    m.add_argument("--csv")
    m.add_argument("--col")
    m.add_argument("--conf", type=float, default=0.95)
    p = sub.add_parser("prop")
    p.add_argument("--x", type=int, required=True)
    p.add_argument("--n", type=int, required=True)
    p.add_argument("--conf", type=float, default=0.95)
    s = sub.add_parser("size")
    s.add_argument("--kind", choices=["mean", "prop"], required=True)
    s.add_argument("--sd", type=float)
    s.add_argument("--p", type=float, default=0.5)
    s.add_argument("--margin", type=float, required=True)
    s.add_argument("--conf", type=float, default=0.95)
    s.add_argument("--population", type=float)
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.cmd == "mean":
        if a.csv:
            import pandas as pd
            v = pd.read_csv(a.csv)[a.col].dropna()
            a.mean, a.sd, a.n = float(v.mean()), float(v.std(ddof=1)), len(v)
        if None in (a.mean, a.sd, a.n):
            ap.error("mean needs --mean --sd --n, or --csv --col")
        lo, hi, half = t_interval(a.mean, a.sd, a.n, a.conf)
        print(f"mean {a.mean:.4g} from {a.n} observations: {a.conf:.0%} CI {lo:.4g} to {hi:.4g} (margin of error {half:.4g})")
    elif a.cmd == "prop":
        lo, hi = wilson(a.x, a.n, a.conf)
        wl, wh = wald(a.x, a.n, a.conf)
        print(f"{a.x}/{a.n} = {a.x / a.n:.4f}: Wilson {a.conf:.0%} CI {lo:.4f} to {hi:.4f}   (textbook Wald {max(wl, 0):.4f} to {min(wh, 1):.4f})")
        if a.x < 10 or a.n - a.x < 10:
            print("few events or non-events: prefer the Wilson interval")
    elif a.cmd == "size":
        if a.kind == "mean":
            if a.sd is None:
                ap.error("size --kind mean needs --sd")
            n = size_mean(a.sd, a.margin, a.conf, a.population)
        else:
            n = size_prop(a.p, a.margin, a.conf, a.population)
        print(f"sample needed for a margin of {a.margin:g} at {a.conf:.0%} confidence: {math.ceil(n):,}")
    else:
        ap.error("choose mean, prop, size or --selftest")


if __name__ == "__main__":
    main()
