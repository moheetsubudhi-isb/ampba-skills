#!/usr/bin/env python3
"""Check whether a linear or logistic model's coefficients can be read.

Standardises numeric features, one-hot encodes categories (dropping one level),
fits an almost unpenalised model, and reports per feature: the standardised
coefficient, the odds ratio (logistic only), the variance inflation factor, and
whether cross-validated Lasso keeps the feature.

  python3 coef_check.py --csv loans.csv --target defaulted
  python3 coef_check.py --selftest
Needs numpy, pandas and scikit-learn.
"""
import argparse
import sys

try:
    import numpy as np
    import pandas as pd
    from sklearn.linear_model import LassoCV, LinearRegression, LogisticRegression, LogisticRegressionCV, RidgeCV
    from sklearn.preprocessing import StandardScaler
except ImportError:
    sys.exit("needs numpy, pandas and scikit-learn: pip install numpy pandas scikit-learn")


def vif(X):
    """1 / (1 - R^2) from regressing each column on all the others."""
    out = {}
    for c in X.columns:
        others = X.drop(columns=c)
        r2 = LinearRegression().fit(others, X[c]).score(others, X[c]) if others.shape[1] else 0.0
        out[c] = np.inf if r2 >= 1 - 1e-12 else 1 / (1 - r2)
    return pd.Series(out)


def check(X, y, classify, seed=0):
    Xs = pd.DataFrame(StandardScaler().fit_transform(X), columns=X.columns, index=X.index)
    if classify:
        coef = LogisticRegression(C=1e6, max_iter=5000).fit(Xs, y).coef_[0]
        kept = LogisticRegressionCV(penalty="l1", solver="saga", cv=5, max_iter=5000, random_state=seed).fit(Xs, y).coef_[0]
    else:
        coef = LinearRegression().fit(Xs, y).coef_
        kept = LassoCV(cv=5, random_state=seed).fit(Xs, y).coef_
    t = pd.DataFrame({"std_coef": coef, "vif": vif(Xs), "lasso_keeps": np.abs(kept) > 1e-6}, index=X.columns)
    if classify:
        t.insert(1, "odds_ratio_per_sd", np.exp(coef))
    return t.sort_values("std_coef", key=np.abs, ascending=False)


def selftest():
    rng = np.random.default_rng(1)
    n = 2000
    x1 = rng.normal(size=n)
    X = pd.DataFrame({"x1": x1, "x1_copy": x1 + rng.normal(scale=0.02, size=n),
                      "unrelated": rng.normal(size=n)})
    y = 3 * x1 + rng.normal(scale=1.0, size=n)
    t = check(X, y, classify=False)
    assert t.loc["x1", "vif"] > 100 and t.loc["x1_copy", "vif"] > 100, "near-duplicate features have huge VIF"
    assert t.loc["unrelated", "vif"] < 1.1
    assert abs(t.loc["x1", "std_coef"] + t.loc["x1_copy", "std_coef"] - 3) < 0.2, "the pair's total effect is stable"
    assert not t.loc["unrelated", "lasso_keeps"] or abs(t.loc["unrelated", "std_coef"]) < 0.1
    ridge = RidgeCV(alphas=[10.0]).fit(StandardScaler().fit_transform(X), y).coef_
    assert abs(ridge[0] - ridge[1]) < 0.3, "Ridge shares credit between correlated features"

    yb = (x1 + rng.normal(scale=1.0, size=n) > 0).astype(int)
    tb = check(X[["x1", "unrelated"]], yb, classify=True)
    assert np.isclose(tb.loc["x1", "odds_ratio_per_sd"], np.exp(tb.loc["x1", "std_coef"]))
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--csv")
    ap.add_argument("--target")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not (a.csv and a.target):
        ap.error("--csv and --target are required")
    df = pd.read_csv(a.csv).dropna()
    y = df.pop(a.target)
    X = pd.get_dummies(df, drop_first=True).astype(float)
    X = X.loc[:, X.std() > 0]
    classify = y.nunique() == 2
    if classify:
        y = (y == sorted(y.unique())[-1]).astype(int)
    t = check(X, y, classify)
    print(f"{len(X):,} rows, {X.shape[1]} features (standardised). VIF above 10: do not read that coefficient alone.\n")
    print(t.round(3).to_string())


if __name__ == "__main__":
    main()
