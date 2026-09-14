#!/usr/bin/env python3
"""Audit a CSV for problems that silently ruin models.

Flags duplicates, mostly-missing, constant, ID-like and text-stored-number
columns, heavy skew, sentinel values, target imbalance, possible target
leakage (a single feature that predicts the target almost perfectly on its
own) and, with --time-col, features whose level shifts between the earliest
and latest third of the data.

  python3 audit_data.py --csv loans.csv --target defaulted --time-col application_date
  python3 audit_data.py --selftest
Needs numpy, pandas and scikit-learn.
"""
import argparse
import sys

try:
    import numpy as np
    import pandas as pd
    from sklearn.model_selection import cross_val_score
    from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
except ImportError:
    sys.exit("needs numpy, pandas and scikit-learn: pip install numpy pandas scikit-learn")

SENTINELS = (-1, -999, 999, 9999, 99999, 999999)
LEAK_SAMPLE = 20_000


def as_numeric(s):
    if pd.api.types.is_numeric_dtype(s):
        return s.astype(float)
    return pd.Series(pd.factorize(s)[0], index=s.index, dtype=float).where(s.notna())


def audit(df, target, time_col=None):
    issues = []
    add = lambda sev, col, issue, evidence: issues.append((sev, col, issue, evidence))
    n = len(df)
    dups = int(df.duplicated().sum())
    if dups:
        add("medium", "(rows)", "duplicate rows", f"{dups} exact duplicates")
    y = df[target]
    if y.isna().any():
        add("high", target, "missing target", f"{int(y.isna().sum())} rows without a label")
    classification = y.nunique() <= 20
    if classification:
        share = y.value_counts(normalize=True)
        if share.min() < 0.1:
            add("medium", target, "imbalanced classes", f"smallest class {share.min():.1%}")
    features = [c for c in df.columns if c not in (target, time_col)]
    for c in features:
        s = df[c]
        miss, nun = s.isna().mean(), s.nunique(dropna=True)
        if miss > 0.3:
            add("medium", c, "mostly missing", f"{miss:.0%} missing")
        if nun <= 1:
            add("low", c, "constant", f"{nun} distinct value")
            continue
        if nun / max(n, 1) > 0.95:
            add("medium", c, "ID-like column", f"{nun} distinct values in {n} rows")
        if s.dtype == object and pd.to_numeric(s, errors="coerce").notna().mean() > 0.9:
            add("low", c, "numbers stored as text", "over 90% parse as numbers")
        if pd.api.types.is_numeric_dtype(s) and nun > 2:
            hits = int(s.isin(SENTINELS).sum())
            if hits > 0.01 * n:
                add("medium", c, "sentinel values", f"{hits} rows use codes like -1 or 999")
            if abs(s.skew()) > 2:
                add("low", c, "heavily skewed", f"skew {s.skew():.1f}; consider log1p")
    known = df[y.notna()]
    if len(known) > LEAK_SAMPLE:
        known = known.sample(LEAK_SAMPLE, random_state=0)
    ky = known[target]
    binary = classification and ky.nunique() == 2
    for c in features:
        x = as_numeric(known[c])
        x = x.fillna(x.median() if x.notna().any() else 0).to_numpy().reshape(-1, 1)
        if classification:
            model, scoring, bar = DecisionTreeClassifier(max_depth=3, random_state=0), ("roc_auc" if binary else "balanced_accuracy"), 0.95
        else:
            model, scoring, bar = DecisionTreeRegressor(max_depth=3, random_state=0), "r2", 0.9
        score = cross_val_score(model, x, ky, cv=3, scoring=scoring).mean()
        if score >= bar:
            add("high", c, "possible target leakage", f"alone scores {scoring} {score:.3f}")
    if time_col:
        ordered = df.assign(_t=pd.to_datetime(df[time_col], errors="coerce")).dropna(subset=["_t"]).sort_values("_t")
        third = len(ordered) // 3
        early, late = ordered.iloc[:third], ordered.iloc[-third:]
        for c in features:
            if pd.api.types.is_numeric_dtype(df[c]):
                sd = ordered[c].std()
                if sd and abs(late[c].mean() - early[c].mean()) / sd > 0.5:
                    add("medium", c, "shifts over time", "latest third differs from earliest by over 0.5 sd")
    return issues


def selftest():
    rng = np.random.default_rng(0)
    n = 1000
    y = (rng.random(n) < 0.3).astype(int)
    df = pd.DataFrame({
        "leak": y + rng.normal(0, 0.01, n),
        "signal": y * 0.5 + rng.normal(0, 1, n),
        "row_id": np.arange(n),
        "constant": 1,
        "sparse": np.where(rng.random(n) < 0.5, np.nan, rng.normal(0, 1, n)),
        "amount": rng.lognormal(0, 2, n),
        "target": y,
    })
    found = {(col, issue) for _, col, issue, _ in audit(df, "target")}
    assert ("leak", "possible target leakage") in found
    assert ("signal", "possible target leakage") not in found
    assert ("row_id", "ID-like column") in found
    assert ("constant", "constant") in found
    assert ("sparse", "mostly missing") in found
    assert ("amount", "heavily skewed") in found
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--csv")
    ap.add_argument("--target")
    ap.add_argument("--time-col")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.csv or not a.target:
        ap.error("--csv and --target are required")
    df = pd.read_csv(a.csv)
    print(f"{len(df)} rows, {df.shape[1]} columns")
    issues = audit(df, a.target, a.time_col)
    order = {"high": 0, "medium": 1, "low": 2}
    for sev, col, issue, evidence in sorted(issues, key=lambda i: order[i[0]]):
        print(f"[{sev:6}] {col}: {issue} ({evidence})")
    if not issues:
        print("no mechanical issues found; still confirm label definition and prediction-time availability")


if __name__ == "__main__":
    main()
