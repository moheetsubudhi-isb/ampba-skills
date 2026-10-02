#!/usr/bin/env python3
"""Give an honest range for one prediction, and check that the range is honest.

  python3 prediction_interval.py --csv houses.csv --outcome price --predictors sqft bedrooms \
      --at sqft=2000 bedrooms=3
  python3 prediction_interval.py --csv houses.csv --outcome price --predictors sqft bedrooms \
      --coverage
  python3 prediction_interval.py --selftest

--at:       for the given inputs, prints the estimate, the confidence interval for the
            AVERAGE outcome of such units, and the prediction interval for ONE unit.
--coverage: holds out a random 30% of rows, builds 95% prediction intervals from the rest
            (regression-based and a split-conformal version that assumes less) and
            reports how often the held-out outcomes really fall inside.
Needs numpy; pandas is needed for --csv.
"""
import argparse
import math
import sys

try:
    import numpy as np
except ImportError:
    sys.exit("needs numpy and pandas: pip install numpy pandas")

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




def fit(X, y):
    A = np.column_stack([np.ones(len(y)), X])
    XtXi = np.linalg.inv(A.T @ A)
    beta = XtXi @ A.T @ y
    resid = y - A @ beta
    dof = len(y) - A.shape[1]
    return {"beta": beta, "XtXi": XtXi, "s2": resid @ resid / dof, "dof": dof, "resid": resid}


def intervals(m, x_new, conf=0.95):
    a = np.concatenate([[1.0], np.asarray(x_new, float)])
    yhat = float(a @ m["beta"])
    lever = float(a @ m["XtXi"] @ a)
    c = t_ppf(0.5 + conf / 2, m["dof"])
    se_mean = math.sqrt(m["s2"] * lever)
    se_one = math.sqrt(m["s2"] * (1 + lever))
    return yhat, (yhat - c * se_mean, yhat + c * se_mean), (yhat - c * se_one, yhat + c * se_one)


def coverage(X, y, conf=0.95, seed=0):
    rng = np.random.default_rng(seed)
    idx = rng.permutation(len(y))
    n_test = int(0.3 * len(y))
    test, rest = idx[:n_test], idx[n_test:]
    cal_n = len(rest) // 3
    cal, train = rest[:cal_n], rest[cal_n:]
    m = fit(X[train], y[train])
    hits_reg = 0
    for i in test:
        _, _, (lo, hi) = intervals(m, X[i], conf)
        hits_reg += lo <= y[i] <= hi
    pred_cal = np.column_stack([np.ones(len(cal)), X[cal]]) @ m["beta"]
    scores = np.sort(np.abs(y[cal] - pred_cal))
    q = scores[min(int(math.ceil((len(cal) + 1) * conf)) - 1, len(cal) - 1)]
    pred_test = np.column_stack([np.ones(len(test)), X[test]]) @ m["beta"]
    hits_conf = (np.abs(y[test] - pred_test) <= q).sum()
    return hits_reg / len(test), hits_conf / len(test), len(test)


def selftest():
    rng = np.random.default_rng(4)
    n = 400
    x = rng.uniform(0, 10, (n, 1))
    y = 5 + 3 * x[:, 0] + rng.normal(0, 4, n)
    m = fit(x, y)
    _, ci, pi = intervals(m, [5.0])
    assert (pi[1] - pi[0]) > 5 * (ci[1] - ci[0]), "the range for one unit is far wider than the range for the average"
    big_x = rng.uniform(0, 10, (40000, 1))
    big_y = 5 + 3 * big_x[:, 0] + rng.normal(0, 4, 40000)
    mb = fit(big_x, big_y)
    _, cib, pib = intervals(mb, [5.0])
    assert (cib[1] - cib[0]) < 0.1 and abs((pib[1] - pib[0]) - 2 * 1.96 * 4) < 0.5, "more data shrinks the first range but never the second"
    _, _, pi_far = intervals(m, [30.0])
    assert (pi_far[1] - pi_far[0]) > (pi[1] - pi[0]) * 1.05, "ranges widen away from typical inputs"
    hits = 0
    for _ in range(300):
        xi = rng.uniform(0, 10)
        yi = 5 + 3 * xi + rng.normal(0, 4)
        _, _, (lo, hi) = intervals(m, [xi])
        hits += lo <= yi <= hi
    assert 0.91 < hits / 300 < 0.99, "a 95% prediction interval covers about 95% of new outcomes"
    xs = rng.uniform(0, 10, (6000, 1))
    ys = 5 + 3 * xs[:, 0] + rng.normal(0, 1, 6000) * (0.3 + xs[:, 0] / 2)
    mh = fit(xs[:3000], ys[:3000])
    inside = np.array([intervals(mh, xs[i])[2][0] <= ys[i] <= intervals(mh, xs[i])[2][1] for i in range(3000, 6000)])
    xt = xs[3000:, 0]
    assert inside.mean() > 0.90, "overall coverage looks fine"
    assert inside[xt > 8].mean() < 0.93 and inside[xt < 2].mean() > 0.99, "but it over-covers where spread is small and under-covers where it is large"
    reg, conf, _ = coverage(xs, ys)
    assert 0.90 < conf < 0.99, "a held-out coverage check is the honest test"
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--csv")
    ap.add_argument("--outcome")
    ap.add_argument("--predictors", nargs="*")
    ap.add_argument("--at", nargs="*", help="values like sqft=2000 bedrooms=3")
    ap.add_argument("--conf", type=float, default=0.95)
    ap.add_argument("--coverage", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not (a.csv and a.outcome and a.predictors):
        ap.error("--csv, --outcome and --predictors are required")
    import pandas as pd
    df = pd.read_csv(a.csv).dropna(subset=[a.outcome] + a.predictors)
    X, y = df[a.predictors].to_numpy(float), df[a.outcome].to_numpy(float)
    if a.at:
        vals = dict(kv.split("=") for kv in a.at)
        x_new = [float(vals[p]) for p in a.predictors]
        yhat, ci, pi = intervals(fit(X, y), x_new, a.conf)
        print(f"estimate {yhat:.4g}")
        print(f"{a.conf:.0%} confidence interval for the AVERAGE {a.outcome} of such units: {ci[0]:.4g} to {ci[1]:.4g}")
        print(f"{a.conf:.0%} prediction interval for ONE unit: {pi[0]:.4g} to {pi[1]:.4g}")
        lo, hi = X.min(0), X.max(0)
        if any(v < l or v > h for v, l, h in zip(x_new, lo, hi)):
            print("warning: these inputs lie outside the range of the data; the interval is unreliable there")
    if a.coverage:
        reg, conf, n_test = coverage(X, y, a.conf)
        print(f"held-out rows: {n_test}. Share inside the {a.conf:.0%} interval: regression-based {reg:.1%}, split-conformal {conf:.1%}")
        if reg < a.conf - 0.05:
            print("the regression-based interval is too narrow for these data; use the conformal or residual-quantile range")
    if not (a.at or a.coverage):
        ap.error("give --at or --coverage")


if __name__ == "__main__":
    main()
