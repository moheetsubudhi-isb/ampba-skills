#!/usr/bin/env python3
"""Estimate price elasticities with a log-log model, and price a promotion.

Fits ln(units) on ln(price), optionally with a promotion flag and its
interaction (regular vs promotional elasticity), a competitor's ln(price)
(cross-elasticity) and extra controls. Also runs the pooled model without the
promotion terms, so the blending bias is visible.

  python3 elasticity_fit.py --csv weekly.csv --units units --price price --promo on_deal \
      --cross rival_price --controls display week_of_year
  python3 elasticity_fit.py --breakeven --margin 0.30 --discount 0.10 --elasticity -2.5
  python3 elasticity_fit.py --selftest
Needs numpy and pandas. p-values use a normal approximation (fine above ~50 rows).
"""
import argparse
import sys
from statistics import NormalDist

try:
    import numpy as np
    import pandas as pd
except ImportError:
    sys.exit("needs numpy and pandas: pip install numpy pandas")


def ols(y, X, names):
    X = np.column_stack([np.ones(len(y)), X])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    dof = max(len(y) - X.shape[1], 1)
    cov = (resid @ resid / dof) * np.linalg.pinv(X.T @ X)
    se = np.sqrt(np.diag(cov))
    p = [2 * (1 - NormalDist().cdf(abs(b / s))) if s > 0 else np.nan for b, s in zip(beta, se)]
    r2 = 1 - (resid @ resid) / ((y - y.mean()) @ (y - y.mean()))
    table = pd.DataFrame({"estimate": beta, "std_err": se, "p_value": p}, index=["intercept"] + names)
    return table, r2, cov


def fit(df, units, price, promo=None, cross=None, controls=()):
    d = df[(df[units] > 0) & (df[price] > 0)].copy()
    y = np.log(d[units].to_numpy(float))
    lnp = np.log(d[price].to_numpy(float))
    cols, names = [lnp], ["ln_price"]
    if promo:
        flag = d[promo].to_numpy(float)
        cols += [flag, flag * lnp]
        names += ["promo", "promo_x_ln_price"]
    if cross:
        cols.append(np.log(d[cross].to_numpy(float)))
        names.append("ln_cross_price")
    for c in controls:
        cols.append(d[c].to_numpy(float))
        names.append(c)
    table, r2, cov = ols(y, np.column_stack(cols), names)
    out = {"table": table, "r2": r2, "rows": len(d), "dropped_zero_or_missing": len(df) - len(d)}
    if promo:
        i, j = names.index("ln_price") + 1, names.index("promo_x_ln_price") + 1
        out["regular"] = table.loc["ln_price", "estimate"]
        out["promotional"] = out["regular"] + table.loc["promo_x_ln_price", "estimate"]
        out["promotional_se"] = float(np.sqrt(cov[i, i] + cov[j, j] + 2 * cov[i, j]))
        out["interaction_p"] = table.loc["promo_x_ln_price", "p_value"]
        pooled, _, _ = ols(y, lnp.reshape(-1, 1), ["ln_price"])
        out["pooled"] = pooled.loc["ln_price", "estimate"]
    return out


def breakeven(margin, discount, elasticity=None):
    need = discount / (margin - discount) if margin > discount else float("inf")
    expected = (1 - discount) ** elasticity - 1 if elasticity is not None else None
    return need, expected


def simulate(n, deal_share, b_reg, b_promo, seed, noise=0.15):
    rng = np.random.default_rng(seed)
    deal = (rng.random(n) < deal_share).astype(float)
    lnp = np.where(deal == 1, np.log(2.25), np.log(3.0)) + rng.normal(0, 0.08, n)
    base = np.log(3.0)
    # deal weeks also get a display lift of +0.8 in log units
    lnq = 8 + np.where(deal == 1, 0.8 + b_promo * (lnp - base), b_reg * (lnp - base)) + rng.normal(0, noise, n)
    return pd.DataFrame({"units": np.exp(lnq), "price": np.exp(lnp), "deal": deal})


def selftest():
    df = simulate(2000, 0.2, -2.5, -4.0, seed=1)
    r = fit(df, "units", "price", promo="deal")
    assert abs(r["regular"] + 2.5) < 0.2, r["regular"]
    assert abs(r["promotional"] + 4.0) < 0.5, r["promotional"]
    assert r["interaction_p"] < 0.01
    assert r["pooled"] < -3.5, f"pooled blends regimes and looks far more elastic ({r['pooled']:.2f})"

    small = simulate(120, 0.08, -2.5, -3.0, seed=4, noise=0.25)
    s = fit(small, "units", "price", promo="deal")
    assert s["interaction_p"] > 0.05, "a real but small promo difference is not proven with few deal weeks"

    need, expected = breakeven(0.30, 0.10, -2.5)
    assert abs(need - 0.5) < 1e-9, "10% off a 30% margin needs +50% volume to break even"
    assert expected < need, "an elasticity of -2.5 predicts only about +30%: the promotion loses money"
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--csv")
    ap.add_argument("--units")
    ap.add_argument("--price")
    ap.add_argument("--promo")
    ap.add_argument("--cross")
    ap.add_argument("--controls", nargs="*", default=[])
    ap.add_argument("--breakeven", action="store_true")
    ap.add_argument("--margin", type=float, help="gross margin as a share of price, e.g. 0.30")
    ap.add_argument("--discount", type=float, help="discount as a share of price, e.g. 0.10")
    ap.add_argument("--elasticity", type=float)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.breakeven:
        if a.margin is None or a.discount is None:
            ap.error("--breakeven needs --margin and --discount")
        need, expected = breakeven(a.margin, a.discount, a.elasticity)
        print(f"{a.discount:.0%} off at a {a.margin:.0%} margin needs +{need:.0%} units to break even on gross profit")
        if expected is not None:
            verdict = "pays for itself" if expected >= need else "loses gross profit"
            print(f"elasticity {a.elasticity} predicts +{expected:.0%} units: the promotion {verdict}")
        return
    if not (a.csv and a.units and a.price):
        ap.error("--csv, --units and --price are required")
    r = fit(pd.read_csv(a.csv), a.units, a.price, a.promo, a.cross, a.controls)
    print(f"{r['rows']:,} rows used ({r['dropped_zero_or_missing']:,} dropped for zero or missing units/price), R-squared {r['r2']:.3f}\n")
    print(r["table"].round(4).to_string())
    if a.promo:
        print(f"\nregular elasticity      {r['regular']:.2f}")
        print(f"promotional elasticity  {r['promotional']:.2f}  (se {r['promotional_se']:.2f})")
        print(f"difference p-value      {r['interaction_p']:.3f}")
        print(f"pooled (ignoring promo) {r['pooled']:.2f}   <- do not set everyday prices from this")
    if a.cross:
        c = r["table"].loc["ln_cross_price", "estimate"]
        print(f"\ncross-price elasticity {c:.2f}: {'substitutes' if c > 0 else 'complements'}")


if __name__ == "__main__":
    main()
