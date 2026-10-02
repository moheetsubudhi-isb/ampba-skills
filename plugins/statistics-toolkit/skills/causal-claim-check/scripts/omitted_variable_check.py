#!/usr/bin/env python3
"""Show how much a treatment effect moves when controls are added, and why.

  python3 omitted_variable_check.py --csv campaign.csv --outcome sales --treatment ad_spend \
      --controls past_sales city_size season
  python3 omitted_variable_check.py --selftest

Prints the treatment coefficient (1) with no controls, (2) adding each control on its
own, (3) with all controls, then checks the identity
    naive effect = adjusted effect + (control's effect on the outcome)
                                     x (how the control moves with the treatment)
and a balance table: how different the treated and untreated (or high and low) rows
are on each control before any adjustment.
A coefficient that moves a lot is evidence of selection bias among OBSERVED
variables; it says nothing about variables you did not measure.
Needs numpy and pandas.
"""
import argparse
import sys

try:
    import numpy as np
except ImportError:
    sys.exit("needs numpy and pandas: pip install numpy pandas")


def ols(y, cols):
    X = np.column_stack([np.ones(len(y))] + list(cols))
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return beta


def coef_table(y, x, controls):
    rows = [("no controls", ols(y, [x])[1])]
    identity = []
    naive = rows[0][1]
    for name, z in controls.items():
        beta = ols(y, [x, z])
        delta = ols(z, [x])[1]
        rows.append((f"+ {name}", beta[1]))
        identity.append((name, naive, beta[1], beta[2], delta, beta[1] + beta[2] * delta))
    if controls:
        rows.append(("all controls", ols(y, [x] + list(controls.values()))[1]))
    return rows, identity


def balance(x, controls):
    binary = set(np.unique(x)) <= {0, 1}
    out = []
    for name, z in controls.items():
        if binary:
            diff = z[x == 1].mean() - z[x == 0].mean()
            out.append((name, diff / z.std(ddof=1)))
        else:
            out.append((name, float(np.corrcoef(x, z)[0, 1])))
    return out, binary


def selftest():
    rng = np.random.default_rng(2)
    n = 20000
    z = rng.normal(size=n)
    x = 0.8 * z + rng.normal(size=n)
    y = 1.0 * x + 2.0 * z + rng.normal(size=n)
    rows, ident = coef_table(y, x, {"z": z})
    naive, adj = rows[0][1], rows[-1][1]
    assert naive > 1.8 and abs(adj - 1.0) < 0.05, "leaving out a confounder inflates the effect"
    _, nv, bh, b2, dl, rhs = ident[0]
    assert np.isclose(nv, rhs), "naive = adjusted + (control's effect) x (control's link to treatment), exactly"

    x_r = rng.normal(size=n)
    y_r = 1.0 * x_r + 2.0 * z + rng.normal(size=n)
    rows_r, _ = coef_table(y_r, x_r, {"z": z})
    assert abs(rows_r[0][1] - rows_r[-1][1]) < 0.05, "with random assignment, adding controls changes little"

    x_f = z + rng.normal(size=n)
    y_f = -1.0 * x_f + 3.0 * z + rng.normal(size=n)
    rows_f, _ = coef_table(y_f, x_f, {"z": z})
    assert rows_f[0][1] > 0.3 and rows_f[-1][1] < -0.8, "a confounder can flip the sign of the raw relationship"

    w = x_r + y_r + rng.normal(size=n)
    rows_c, _ = coef_table(y_r, x_r, {"w": w})
    assert abs(rows_c[0][1] - 1.0) < 0.05 and abs(rows_c[-1][1] - 1.0) > 0.3, "controlling for an outcome of both biases a clean estimate"
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--csv")
    ap.add_argument("--outcome")
    ap.add_argument("--treatment")
    ap.add_argument("--controls", nargs="*", default=[])
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not (a.csv and a.outcome and a.treatment):
        ap.error("--csv, --outcome and --treatment are required")
    import pandas as pd
    df = pd.read_csv(a.csv).dropna(subset=[a.outcome, a.treatment] + a.controls)
    y, x = df[a.outcome].to_numpy(float), df[a.treatment].to_numpy(float)
    controls = {c: df[c].to_numpy(float) for c in a.controls}
    rows, identity = coef_table(y, x, controls)
    print(f"{len(df):,} rows. Coefficient on {a.treatment}:")
    for label, b in rows:
        print(f"  {label:<24} {b:+.4g}")
    if identity:
        print("\nidentity check, one control at a time: naive = adjusted + control effect x link to treatment")
        for name, naive, adj, b2, delta, rhs in identity:
            print(f"  {name:<20} {naive:+.4g} = {adj:+.4g} + ({b2:+.4g} x {delta:+.4g}) = {rhs:+.4g}")
        bal, binary = balance(x, controls)
        print("\nbalance before adjustment (" + ("standardised difference, treated minus untreated" if binary else "correlation with treatment") + ")")
        for name, v in bal:
            print(f"  {name:<20} {v:+.2f}" + ("   <- groups differ" if abs(v) > (0.1 if binary else 0.2) else ""))
        first, last = rows[0][1], rows[-1][1]
        move = abs(first - last) / abs(first) if first else float("inf")
        print(f"\nadding the controls moved the estimate by {move:.0%}. "
              + ("Treatment was tied to these variables: the raw comparison was contaminated." if move > 0.25
                 else "Little movement on these controls; unmeasured variables can still bias it."))


if __name__ == "__main__":
    main()
