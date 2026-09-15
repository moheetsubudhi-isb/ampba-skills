#!/usr/bin/env python3
"""Compare a regression model's errors with a baseline, overall and by segment.

Reports MAE, RMSE, MAPE (skipping zero actuals, and saying how many), WAPE,
R-squared and bias (mean of prediction minus actual). Without --baseline, the
baseline predicts the mean actual; that is an in-sample mean, so prefer a real
baseline column such as last period's value.

  python3 regression_error_check.py --csv test_preds.csv --actual y --pred y_hat --baseline last_week --segment region
  python3 regression_error_check.py --selftest
Needs numpy and pandas.
"""
import argparse
import sys

try:
    import numpy as np
    import pandas as pd
except ImportError:
    sys.exit("needs numpy and pandas: pip install numpy pandas")


def metrics(actual, pred):
    a, p = np.asarray(actual, float), np.asarray(pred, float)
    err = p - a
    nonzero = a != 0
    ss_tot = ((a - a.mean()) ** 2).sum()
    return {
        "mae": np.abs(err).mean(),
        "rmse": np.sqrt((err ** 2).mean()),
        "mape": np.abs(err[nonzero] / a[nonzero]).mean() if nonzero.any() else np.nan,
        "mape_rows_skipped": int((~nonzero).sum()),
        "wape": np.abs(err).sum() / np.abs(a).sum() if np.abs(a).sum() else np.nan,
        "r2": 1 - (err ** 2).sum() / ss_tot if ss_tot else np.nan,
        "bias": err.mean(),
        "n": len(a),
    }


def report(df, actual, pred, baseline=None, segment=None):
    base = df[baseline] if baseline else pd.Series(df[actual].mean(), index=df.index)
    rows = {"model": metrics(df[actual], df[pred]), "baseline": metrics(df[actual], base)}
    table = pd.DataFrame(rows).T
    seg = None
    if segment:
        seg = df.groupby(segment).apply(lambda g: pd.Series(metrics(g[actual], g[pred])), include_groups=False)
    return table, seg


def selftest():
    actual = np.array([1, 2, 1, 500, 800, 650, 900], float)
    pred = actual + np.array([3, 3, 3, -3, 3, -3, 3])
    m = metrics(actual, pred)
    assert m["mape"] > 1.0, "a 3-unit miss on actuals of 1 or 2 makes MAPE explode"
    assert m["wape"] < 0.01, "WAPE weighs errors by volume and stays small"
    assert abs(m["mae"] - 3) < 1e-9 and m["r2"] > 0.99

    rng = np.random.default_rng(0)
    y = rng.normal(100, 10, 500)
    worse = y.mean() + rng.normal(0, 15, 500)
    assert metrics(y, worse)["r2"] < 0, "a model worse than predicting the mean has negative R-squared"

    wide = rng.normal(1000, 400, 500)
    wide_pred = wide + rng.normal(0, 60, 500)
    wm = metrics(wide, wide_pred)
    assert wm["r2"] > 0.95 and wm["mae"] > 40, "R-squared can look excellent while errors stay large in units"

    df = pd.DataFrame({"y": [10, 10, 10, 10], "p": [12, 12, 10, 10], "seg": ["a", "a", "b", "b"]})
    _, seg = report(df, "y", "p", segment="seg")
    assert seg.loc["a", "bias"] == 2 and seg.loc["b", "bias"] == 0, "segment view exposes bias the total hides"
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--csv")
    ap.add_argument("--actual")
    ap.add_argument("--pred")
    ap.add_argument("--baseline")
    ap.add_argument("--segment")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not (a.csv and a.actual and a.pred):
        ap.error("--csv, --actual and --pred are required")
    cols = [c for c in [a.actual, a.pred, a.baseline, a.segment] if c]
    df = pd.read_csv(a.csv, usecols=cols).dropna()
    table, seg = report(df, a.actual, a.pred, a.baseline, a.segment)
    label = a.baseline or "mean of actuals (in-sample)"
    print(f"{len(df):,} rows. Baseline: {label}\n")
    print(table.round(4).to_string())
    if seg is not None:
        print(f"\nModel errors by {a.segment}\n")
        print(seg.round(4).to_string())


if __name__ == "__main__":
    main()
