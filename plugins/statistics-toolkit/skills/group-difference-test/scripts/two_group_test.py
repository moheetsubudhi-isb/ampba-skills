#!/usr/bin/env python3
"""Test whether two groups, or two time points, differ by more than chance.

  python3 two_group_test.py means --csv orders.csv --value basket --group region
  python3 two_group_test.py means --a 12,15,11,14 --b 18,17,21,16
  python3 two_group_test.py paired --csv audit.csv --before days_old --after days_new
  python3 two_group_test.py props --a-n 800 --a-x 96 --b-n 760 --b-x 122
  python3 two_group_test.py --selftest

means:  Welch t-test (unequal variances), CI for the difference, standardised effect
        size and a permutation p-value as a cross-check.
paired: t-test on the within-pair differences.
props:  two-proportion z-test with CI for the difference.
Needs numpy. Every result ends with the practical-size reading, not only the p-value.
"""
import argparse
import math
import sys
from statistics import NormalDist

try:
    import numpy as np
except ImportError:
    sys.exit("needs numpy: pip install numpy")

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


def chi2_sf(x, k):
    """P(X > x) for chi-square with k degrees of freedom."""
    if x <= 0:
        return 1.0
    a, z = k / 2, x / 2
    if z < a + 1:
        term = total = 1.0 / a
        n = a
        for _ in range(1000):
            n += 1
            term *= z / n
            total += term
            if abs(term) < abs(total) * 1e-13:
                break
        return 1 - total * math.exp(-z + a * math.log(z) - math.lgamma(a))
    tiny = 1e-300
    b = z + 1 - a
    c = 1 / tiny
    d = 1 / b
    h = d
    for i in range(1, 1000):
        an = -i * (i - a)
        b += 2
        d = an * d + b
        d = d if abs(d) > tiny else tiny
        c = b + an / c
        c = c if abs(c) > tiny else tiny
        d = 1 / d
        delta = d * c
        h *= delta
        if abs(delta - 1) < 1e-13:
            break
    return math.exp(-z + a * math.log(z) - math.lgamma(a)) * h


def welch(a, b, perms=5000, seed=1):
    a, b = np.asarray(a, float), np.asarray(b, float)
    va, vb = a.var(ddof=1) / len(a), b.var(ddof=1) / len(b)
    se = math.sqrt(va + vb)
    diff = b.mean() - a.mean()
    df = (va + vb) ** 2 / (va ** 2 / (len(a) - 1) + vb ** 2 / (len(b) - 1))
    t = diff / se
    p = 2 * t_sf(abs(t), df)
    c = t_ppf(0.975, df)
    sp = math.sqrt(((len(a) - 1) * a.var(ddof=1) + (len(b) - 1) * b.var(ddof=1)) / (len(a) + len(b) - 2))
    pool, rng, cnt = np.concatenate([a, b]), np.random.default_rng(seed), 0
    for _ in range(perms):
        rng.shuffle(pool)
        cnt += abs(pool[len(a):].mean() - pool[:len(a)].mean()) >= abs(diff) - 1e-12
    return {"mean_a": a.mean(), "mean_b": b.mean(), "diff": diff, "ci": (diff - c * se, diff + c * se),
            "t": t, "df": df, "p": p, "d": diff / sp, "p_perm": (cnt + 1) / (perms + 1)}


def paired(before, after):
    d = np.asarray(after, float) - np.asarray(before, float)
    se = d.std(ddof=1) / math.sqrt(len(d))
    t, df = d.mean() / se, len(d) - 1
    c = t_ppf(0.975, df)
    return {"mean_diff": d.mean(), "ci": (d.mean() - c * se, d.mean() + c * se), "t": t, "df": df,
            "p": 2 * t_sf(abs(t), df), "d": d.mean() / d.std(ddof=1)}


def props(an, ax, bn, bx):
    pa, pb = ax / an, bx / bn
    pool = (ax + bx) / (an + bn)
    z = (pb - pa) / math.sqrt(pool * (1 - pool) * (1 / an + 1 / bn))
    se = math.sqrt(pa * (1 - pa) / an + pb * (1 - pb) / bn)
    return {"rate_a": pa, "rate_b": pb, "diff": pb - pa, "ci": (pb - pa - 1.96 * se, pb - pa + 1.96 * se),
            "z": z, "p": 2 * (1 - NormalDist().cdf(abs(z)))}


def size_word(d):
    d = abs(d)
    return "negligible" if d < 0.2 else "small" if d < 0.5 else "medium" if d < 0.8 else "large"


def selftest():
    assert abs(2 * t_sf(2.0, 10) - 0.0734) < 1e-3 and abs(t_ppf(0.975, 10) - 2.228) < 1e-3
    assert abs(chi2_sf(3.841, 1) - 0.05) < 1e-3
    rng = np.random.default_rng(5)
    before = rng.normal(100, 15, 30)
    after = before + 2 + rng.normal(0, 1.5, 30)
    assert welch(before, after)["p"] > 0.05, "treating paired data as independent hides a real shift"
    assert paired(before, after)["p"] < 0.001, "the paired test sees it"
    a, b = rng.normal(50, 10, 40), rng.normal(56, 10, 40)
    w = welch(a, b)
    assert abs(w["p"] - w["p_perm"]) < 0.05, "permutation and Welch agree on well-behaved data"
    big_a, big_b = rng.normal(100, 10, 200000), rng.normal(100.3, 10, 200000)
    w = welch(big_a, big_b)
    assert w["p"] < 0.001 and size_word(w["d"]) == "negligible", "with huge samples a trivial gap is still 'significant'"
    r = props(800, 96, 760, 122)
    assert r["p"] < 0.05 and r["ci"][0] > 0
    print("selftest ok")


def report_means(r, label_a="A", label_b="B"):
    print(f"{label_a} mean {r['mean_a']:.4g}   {label_b} mean {r['mean_b']:.4g}   difference {r['diff']:+.4g}")
    print(f"95% CI for the difference {r['ci'][0]:+.4g} to {r['ci'][1]:+.4g}   Welch t = {r['t']:.2f} (df {r['df']:.1f})   p = {r['p']:.4f}")
    print(f"permutation p = {r['p_perm']:.4f}   standardised effect d = {r['d']:+.2f} ({size_word(r['d'])})")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--selftest", action="store_true")
    sub = ap.add_subparsers(dest="cmd")
    m = sub.add_parser("means")
    m.add_argument("--csv")
    m.add_argument("--value")
    m.add_argument("--group")
    m.add_argument("--a", help="comma-separated values for group A")
    m.add_argument("--b", help="comma-separated values for group B")
    p = sub.add_parser("paired")
    p.add_argument("--csv", required=True)
    p.add_argument("--before", required=True)
    p.add_argument("--after", required=True)
    q = sub.add_parser("props")
    for f in ("a-n", "a-x", "b-n", "b-x"):
        q.add_argument("--" + f, type=float, required=True)
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.cmd == "means":
        if a.csv:
            import pandas as pd
            df = pd.read_csv(a.csv).dropna(subset=[a.value, a.group])
            levels = sorted(df[a.group].unique(), key=str)
            if len(levels) != 2:
                sys.exit(f"'{a.group}' has {len(levels)} levels; this tool compares exactly two. For three or more, see references/which-test.md")
            xa, xb = (df.loc[df[a.group] == lv, a.value] for lv in levels)
            report_means(welch(xa, xb), *map(str, levels))
        elif a.a and a.b:
            report_means(welch([float(x) for x in a.a.split(",")], [float(x) for x in a.b.split(",")]))
        else:
            ap.error("means needs --csv with --value and --group, or --a and --b")
    elif a.cmd == "paired":
        import pandas as pd
        df = pd.read_csv(a.csv).dropna(subset=[a.before, a.after])
        r = paired(df[a.before], df[a.after])
        print(f"{len(df)} pairs   mean change {r['mean_diff']:+.4g}   95% CI {r['ci'][0]:+.4g} to {r['ci'][1]:+.4g}")
        print(f"paired t = {r['t']:.2f} (df {r['df']})   p = {r['p']:.4f}   effect d = {r['d']:+.2f} ({size_word(r['d'])})")
    elif a.cmd == "props":
        r = props(a.a_n, a.a_x, a.b_n, a.b_x)
        print(f"A {r['rate_a']:.4f}   B {r['rate_b']:.4f}   difference {r['diff']:+.4f}")
        print(f"95% CI {r['ci'][0]:+.4f} to {r['ci'][1]:+.4f}   z = {r['z']:.2f}   p = {r['p']:.4f}")
    else:
        ap.error("choose means, paired, props or --selftest")


if __name__ == "__main__":
    main()
