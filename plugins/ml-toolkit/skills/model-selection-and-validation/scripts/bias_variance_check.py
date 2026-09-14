#!/usr/bin/env python3
"""Sweep model complexity and read overfitting or underfitting from the gap.

Cross-validates a decision tree across max_depth and k-nearest neighbours
across k, reporting training score, validation score, the gap between them,
a verdict, and the simplest setting within one standard error of the best.

  python3 bias_variance_check.py --csv churn.csv --target churned
  python3 bias_variance_check.py --selftest
Needs numpy, pandas and scikit-learn.
"""
import argparse
import sys

try:
    import numpy as np
    import pandas as pd
    from sklearn.model_selection import KFold, StratifiedKFold, cross_validate
    from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
except ImportError:
    sys.exit("needs numpy, pandas and scikit-learn: pip install numpy pandas scikit-learn")

GAP_OVERFIT = 0.10
UNDERFIT_MARGIN = 0.05


def families(classification):
    Tree = DecisionTreeClassifier if classification else DecisionTreeRegressor
    Knn = KNeighborsClassifier if classification else KNeighborsRegressor
    return [
        # values run from simplest to most complex
        ("decision tree max_depth", [1, 2, 3, 5, 8, 12, None], lambda d: Tree(max_depth=d, random_state=0)),
        ("knn k", [51, 21, 11, 5, 3, 1], lambda k: make_pipeline(StandardScaler(), Knn(n_neighbors=k))),
    ]


def sweep(X, y, classification):
    cv = (StratifiedKFold if classification else KFold)(5, shuffle=True, random_state=0)
    scoring = "accuracy" if classification else "r2"
    results = {}
    for name, values, make in families(classification):
        rows = []
        for v in values:
            if name.startswith("knn") and v >= len(X) * 0.8:
                continue
            r = cross_validate(make(v), X, y, cv=cv, scoring=scoring, return_train_score=True)
            rows.append({"setting": v, "train": r["train_score"].mean(), "valid": r["test_score"].mean(),
                         "valid_sd": r["test_score"].std()})
        t = pd.DataFrame(rows)
        best = t.valid.max()
        t["gap"] = t.train - t.valid
        t["verdict"] = np.where(t.gap > GAP_OVERFIT, "overfit",
                                np.where(t.valid < best - UNDERFIT_MARGIN, "underfit", "ok"))
        se = t.loc[t.valid.idxmax(), "valid_sd"] / np.sqrt(5)
        simplest = t[t.valid >= best - se].iloc[0]["setting"]
        results[name] = (t, simplest)
    return results


def selftest():
    from sklearn.datasets import make_classification
    X, y = make_classification(800, n_features=10, n_informative=4, flip_y=0.2, random_state=0)
    t, simplest = sweep(X, y, True)["decision tree max_depth"]
    deepest = t[t.setting.isna()].iloc[0]
    assert deepest.verdict == "overfit" and deepest.train > 0.99, "unlimited depth should memorise"
    assert simplest is not None and not pd.isna(simplest), "1-SE rule should prefer a limited depth"
    knn, _ = sweep(X, y, True)["knn k"]
    assert knn[knn.setting == 1].iloc[0].verdict == "overfit", "k=1 should memorise"
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--csv")
    ap.add_argument("--target")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.csv or not a.target:
        ap.error("--csv and --target are required")
    df = pd.read_csv(a.csv).dropna(subset=[a.target])
    y = df[a.target]
    X = pd.get_dummies(df.drop(columns=[a.target]), dummy_na=True).fillna(0).to_numpy(dtype=float)
    classification = y.nunique() <= 20
    print(f"{len(X)} rows, {X.shape[1]} features after one-hot; scoring {'accuracy' if classification else 'R2'}; "
          f"no split design applied, so treat this as a first read, not a final estimate")
    for name, (t, simplest) in sweep(X, y, classification).items():
        print(f"\n{name}  (simplest within 1 SE of best: {simplest})")
        print(t.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
