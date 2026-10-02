#!/usr/bin/env python3
"""Fit a count model, read it as rate ratios, and check whether Poisson is good enough.

  python3 count_model_check.py --csv sales.csv --outcome units --predictors discount region \
      --exposure days_on_shelf
  python3 count_model_check.py --csv claims.csv --outcome claims --predictors age_band --family nb
  python3 count_model_check.py --selftest

Fits Poisson by iteratively reweighted least squares (log link). --exposure names a
column (days, people, customer-months) used as an offset, which turns counts into rates.
--family: poisson (default), quasi (same coefficients, standard errors widened by the
dispersion), or nb (negative binomial with the spread estimated from the data).
Reports rate ratios, the dispersion statistic (near 1 is fine, well above 1 means the
Poisson standard errors are too small), zeros seen against zeros Poisson expects, and AIC.
Needs numpy; pandas is needed for --csv.
"""
import argparse
import math
import sys
from statistics import NormalDist

try:
    import numpy as np
except ImportError:
    sys.exit("needs numpy and pandas: pip install numpy pandas")


def irls(X, y, offset, alpha=0.0, iters=60):
    n, p = X.shape
    beta = np.zeros(p)
    beta[0] = math.log(max(y.mean(), 1e-9)) - (offset.mean() if offset is not None else 0)
    off = offset if offset is not None else np.zeros(n)
    for _ in range(iters):
        mu = np.exp(np.clip(X @ beta + off, -30, 30))
        w = mu / (1 + alpha * mu)
        z = X @ beta + (y - mu) / mu
        new = np.linalg.solve(X.T @ (X * w[:, None]), X.T @ (w * z))
        if np.max(np.abs(new - beta)) < 1e-10:
            beta = new
            break
        beta = new
    mu = np.exp(np.clip(X @ beta + off, -30, 30))
    w = mu / (1 + alpha * mu)
    cov = np.linalg.inv(X.T @ (X * w[:, None]))
    return beta, cov, mu


def loglik(y, mu, alpha=0.0):
    lg = np.vectorize(math.lgamma)
    if alpha <= 0:
        return float(np.sum(y * np.log(mu) - mu - lg(y + 1)))
    r = 1 / alpha
    return float(np.sum(lg(y + r) - lg(r) - lg(y + 1) + r * np.log(r / (r + mu)) + y * np.log(mu / (r + mu))))


def fit_count(X, y, offset=None, family="poisson"):
    A = np.column_stack([np.ones(len(y)), X])
    n, p = A.shape
    beta, cov, mu = irls(A, y, offset)
    phi = float(np.sum((y - mu) ** 2 / mu) / (n - p))
    alpha = 0.0
    if family == "nb":
        alpha = max(float(np.sum((y - mu) ** 2 - mu) / np.sum(mu ** 2)), 1e-6)
        beta, cov, mu = irls(A, y, offset, alpha)
    se = np.sqrt(np.diag(cov))
    if family == "quasi":
        se = se * math.sqrt(max(phi, 1.0))
    ll = loglik(y, mu, alpha)
    return {"beta": beta, "se": se, "mu": mu, "phi": phi, "alpha": alpha, "aic": -2 * ll + 2 * (p + (1 if alpha else 0)),
            "zeros_seen": float((y == 0).mean()), "zeros_expected": float(np.exp(-mu).mean()) if alpha == 0 else float(((1 + alpha * mu) ** (-1 / alpha)).mean())}


def selftest():
    rng = np.random.default_rng(6)
    n = 4000
    x = rng.normal(size=n)
    y = rng.poisson(np.exp(0.5 + 0.4 * x))
    r = fit_count(x[:, None], y)
    assert abs(r["beta"][1] - 0.4) < 0.05 and 0.9 < r["phi"] < 1.1, "on genuine Poisson counts the dispersion is about 1"

    mu = np.exp(0.5 + 0.4 * x) * rng.gamma(shape=1.0, scale=1.0, size=n)
    yo = rng.poisson(mu)
    p_fit, q_fit, nb_fit = (fit_count(x[:, None], yo, family=f) for f in ("poisson", "quasi", "nb"))
    assert p_fit["phi"] > 2, "unmeasured differences between units make counts more spread out than Poisson allows"
    assert q_fit["se"][1] > 1.5 * p_fit["se"][1], "so the Poisson standard errors are too small"
    assert nb_fit["aic"] < p_fit["aic"] - 100, "a negative binomial fits the spread far better"

    grp = np.repeat([0.0, 1.0], n // 2)
    expo = np.where(grp == 1, 30.0, 10.0)
    yc = rng.poisson(0.2 * expo)
    no_off = fit_count(grp[:, None], yc)
    with_off = fit_count(grp[:, None], yc, offset=np.log(expo))
    assert abs(no_off["beta"][1] - math.log(3)) < 0.05, "without an offset the longer-observed group looks three times 'better'"
    assert abs(with_off["beta"][1]) < 0.06, "with the offset the two groups have the same rate"

    yz = rng.poisson(2.0, n) * (rng.random(n) > 0.4)
    z = fit_count(np.zeros((n, 0)), yz)
    assert z["zeros_seen"] - z["zeros_expected"] > 0.15, "far more zeros than Poisson expects points to a two-part model"
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--csv")
    ap.add_argument("--outcome")
    ap.add_argument("--predictors", nargs="*")
    ap.add_argument("--exposure")
    ap.add_argument("--family", choices=["poisson", "quasi", "nb"], default="poisson")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not (a.csv and a.outcome and a.predictors):
        ap.error("--csv, --outcome and --predictors are required")
    import pandas as pd
    cols = [a.outcome] + a.predictors + ([a.exposure] if a.exposure else [])
    df = pd.read_csv(a.csv).dropna(subset=cols)
    X = pd.get_dummies(df[a.predictors], drop_first=True).astype(float)
    y = df[a.outcome].to_numpy(float)
    offset = np.log(df[a.exposure].to_numpy(float)) if a.exposure else None
    r = fit_count(X.to_numpy(), y, offset, a.family)
    names = ["(baseline rate)"] + list(X.columns)
    z95 = NormalDist().inv_cdf(0.975)
    print(f"{len(df):,} rows, family {a.family}" + (f", exposure {a.exposure}" if a.exposure else ""))
    print(f"{'term':<26}{'rate ratio':>12}   95% CI            p")
    for nm, b, s in zip(names, r["beta"], r["se"]):
        p = 2 * (1 - NormalDist().cdf(abs(b / s)))
        if nm.startswith("(baseline"):
            print(f"{nm:<26}{math.exp(b):>12.4g}   (per unit of exposure)" if a.exposure else f"{nm:<26}{math.exp(b):>12.4g}")
        else:
            print(f"{nm:<26}{math.exp(b):>12.4g}   {math.exp(b - z95 * s):.4g} to {math.exp(b + z95 * s):.4g}   {p:.4f}")
    print(f"\ndispersion (Poisson) {r['phi']:.2f}" + ("   <- well above 1: Poisson standard errors are too small; use --family quasi or nb" if r["phi"] > 1.5 and a.family == "poisson" else ""))
    print(f"zeros seen {r['zeros_seen']:.1%}, zeros the model expects {r['zeros_expected']:.1%}"
          + ("   <- many extra zeros: consider a two-part (hurdle or zero-inflated) model" if r["zeros_seen"] - r["zeros_expected"] > 0.1 else ""))
    print(f"AIC {r['aic']:.1f}" + (f"   (negative binomial spread alpha = {r['alpha']:.3f})" if a.family == "nb" else ""))


if __name__ == "__main__":
    main()
