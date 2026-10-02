#!/usr/bin/env python3
"""Check whether a linear regression can be trusted for inference.

  python3 regression_diagnostics.py --csv orders.csv --outcome profit \
      --predictors sales discount quantity segment region
  python3 regression_diagnostics.py --selftest

Fits OLS (text columns become indicator columns with the first level as the
baseline) and prints: the coefficient table with classical and robust (HC3)
standard errors; R-squared, adjusted R-squared, residual standard error and the
overall F test; variance inflation factors; the Breusch-Pagan test for unequal
variance; a normality check on residuals; and the rows with the most leverage
and influence (Cook's distance). It ends with a symptom-to-action list.
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


def f_sf(f, d1, d2):
    return betainc(d2 / 2, d1 / 2, d2 / (d2 + d1 * f))


def fit(y, X, names):
    n, k = X.shape
    A = np.column_stack([np.ones(n), X])
    XtXi = np.linalg.inv(A.T @ A)
    beta = XtXi @ A.T @ y
    resid = y - A @ beta
    dof = n - A.shape[1]
    s2 = resid @ resid / dof
    se = np.sqrt(np.diag(XtXi) * s2)
    h = np.einsum("ij,jk,ik->i", A, XtXi, A)
    meat = (A * (resid / (1 - h))[:, None]).T @ (A * (resid / (1 - h))[:, None])
    se_hc3 = np.sqrt(np.diag(XtXi @ meat @ XtXi))
    sst = ((y - y.mean()) ** 2).sum()
    r2 = 1 - (resid @ resid) / sst
    adj = 1 - (1 - r2) * (n - 1) / dof
    fstat = (r2 / k) / ((1 - r2) / dof) if k else float("nan")
    cook = resid ** 2 / (A.shape[1] * s2) * h / (1 - h) ** 2
    vif = {}
    for j, name in enumerate(names):
        others = np.delete(X, j, axis=1)
        if others.shape[1]:
            B = np.column_stack([np.ones(n), others])
            r = X[:, j] - B @ np.linalg.lstsq(B, X[:, j], rcond=None)[0]
            r2j = 1 - (r @ r) / ((X[:, j] - X[:, j].mean()) ** 2).sum()
            vif[name] = 1 / (1 - r2j) if r2j < 1 else float("inf")
        else:
            vif[name] = 1.0
    # Breusch-Pagan, studentised: n * R-squared of squared residuals on the predictors
    e2 = resid ** 2
    g = np.linalg.lstsq(A, e2, rcond=None)[0]
    r2_aux = 1 - ((e2 - A @ g) ** 2).sum() / ((e2 - e2.mean()) ** 2).sum()
    bp = n * r2_aux
    skew = ((resid / resid.std()) ** 3).mean()
    kurt = ((resid / resid.std()) ** 4).mean()
    jb = n / 6 * (skew ** 2 + (kurt - 3) ** 2 / 4)
    return {"n": n, "k": k, "dof": dof, "beta": beta, "se": se, "se_hc3": se_hc3, "r2": r2, "adj": adj,
            "rse": math.sqrt(s2), "f": fstat, "f_p": f_sf(fstat, k, dof) if k else float("nan"),
            "vif": vif, "bp": bp, "bp_p": chi2_sf(bp, k), "skew": skew, "kurt": kurt, "jb_p": math.exp(-jb / 2),
            "leverage": h, "cook": cook, "resid": resid, "names": ["(intercept)"] + list(names)}


def selftest():
    assert abs(f_sf(4.965, 1, 10) - 0.05) < 1e-3
    rng = np.random.default_rng(8)
    n = 600
    x1, x2 = rng.normal(size=n), rng.normal(size=n)
    y = 1 + 2 * x1 - x2 + rng.normal(size=n)
    r = fit(y, np.column_stack([x1, x2]), ["x1", "x2"])
    assert abs(r["beta"][1] - 2) < 0.15 and r["bp_p"] > 0.01 and r["jb_p"] > 0.01 and max(r["vif"].values()) < 1.2

    xh = rng.uniform(1, 10, n)
    yh = 3 + 2 * xh + rng.normal(size=n) * xh ** 1.5 / 3
    rh = fit(yh, xh[:, None], ["x"])
    assert rh["bp_p"] < 0.001, "a fan-shaped residual plot is caught by the Breusch-Pagan test"
    assert abs(rh["se_hc3"][1] / rh["se"][1] - 1) > 0.10, "robust standard errors differ when variance is unequal"

    xc = rng.normal(size=n)
    xc2 = xc + rng.normal(size=n) * 0.05
    yc = 1 + xc + rng.normal(size=n)
    rc = fit(yc, np.column_stack([xc, xc2]), ["a", "b"])
    r1 = fit(yc, xc[:, None], ["a"])
    assert rc["vif"]["a"] > 100 and rc["se"][1] > 5 * r1["se"][1], "collinearity inflates standard errors"
    assert abs(rc["rse"] - r1["rse"]) < 0.02, "but the predictions hardly change"

    xs = rng.normal(size=50)
    ys = 2 * xs + rng.normal(size=50) * 0.5
    xs[0], ys[0] = 6.0, -8.0
    rs = fit(ys, xs[:, None], ["x"])
    assert rs["cook"].argmax() == 0 and rs["cook"][0] > 4 / 50, "one extreme row is flagged by Cook's distance"
    clean = fit(ys[1:], xs[1:, None], ["x"])
    assert abs(rs["beta"][1] - clean["beta"][1]) > 0.5, "and it moves the slope a long way"
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--csv")
    ap.add_argument("--outcome")
    ap.add_argument("--predictors", nargs="*")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not (a.csv and a.outcome and a.predictors):
        ap.error("--csv, --outcome and --predictors are required")
    import pandas as pd
    df = pd.read_csv(a.csv).dropna(subset=[a.outcome] + a.predictors)
    X = pd.get_dummies(df[a.predictors], drop_first=True).astype(float)
    r = fit(df[a.outcome].to_numpy(float), X.to_numpy(), list(X.columns))
    print(f"{r['n']:,} rows, {r['k']} predictors, {r['dof']} residual degrees of freedom\n")
    print(f"{'term':<26}{'estimate':>12}{'std err':>11}{'robust':>11}{'t':>8}{'p':>9}   95% CI")
    for nm, b, s, sh in zip(r["names"], r["beta"], r["se"], r["se_hc3"]):
        t = b / s
        p = 2 * t_sf(abs(t), r["dof"])
        c = t_ppf(0.975, r["dof"])
        print(f"{nm:<26}{b:>12.4g}{s:>11.4g}{sh:>11.4g}{t:>8.2f}{p:>9.4f}   {b - c * s:.4g} to {b + c * s:.4g}")
    print(f"\nR-squared {r['r2']:.3f}  adjusted {r['adj']:.3f}  residual std error {r['rse']:.4g}  F p-value {r['f_p']:.3g}")
    print("R-squared and adjusted R-squared are in-sample; they do not measure prediction on new data.")
    notes = []
    big = {k: v for k, v in r["vif"].items() if v > 5}
    print("\nvariance inflation: " + ", ".join(f"{k} {v:.1f}" for k, v in r["vif"].items()))
    if big:
        notes.append(f"High VIF ({', '.join(big)}): coefficients of these are unstable and their standard errors inflated; predictions are not hurt. Combine, drop or penalise them.")
    print(f"Breusch-Pagan p = {r['bp_p']:.4g}" + ("  <- unequal variance" if r["bp_p"] < 0.05 else ""))
    if r["bp_p"] < 0.05:
        notes.append("Unequal variance: use the robust standard errors, transform the outcome, or change the model family.")
    print(f"residual skew {r['skew']:+.2f}, kurtosis {r['kurt']:.2f}, Jarque-Bera p = {r['jb_p']:.4g}")
    if r["jb_p"] < 0.05:
        notes.append("Residuals are not normal. With many rows the coefficients are still fine; look at which tail is heavy and try log(outcome).")
    top = np.argsort(-r["cook"])[:5]
    print("\nmost influential rows (index, Cook's distance, leverage, residual)")
    for i in top:
        flag = "  <- check this row" if r["cook"][i] > 4 / r["n"] else ""
        print(f"  {i:>6}  {r['cook'][i]:.4f}  {r['leverage'][i]:.3f}  {r['resid'][i]:+.4g}{flag}")
    if r["cook"][top[0]] > 4 / r["n"]:
        notes.append("Influential rows: confirm they are real, then refit without them and report both results.")
    print("\nwhat to do next")
    for note in notes or ["Nothing alarming in these checks. Also look at the residual-versus-fitted plot for curves and at how rows are grouped (repeat customers, repeat stores)."]:
        print("  - " + note)


if __name__ == "__main__":
    main()
