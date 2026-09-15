#!/usr/bin/env python3
"""Compare a linear baseline, a tree, bagging, a random forest and gradient boosting.

Reports cross-validated score (ROC-AUC for binary targets, R-squared for
numeric ones), its spread and the training-validation gap for each model, then
random-forest impurity importance beside permutation importance on held-out
rows. Categorical columns are one-hot encoded.

  python3 ensemble_compare.py --csv customers.csv --target churned
  python3 ensemble_compare.py --selftest
Needs numpy, pandas and scikit-learn.
"""
import argparse
import sys

try:
    import numpy as np
    import pandas as pd
    from sklearn.datasets import make_classification
    from sklearn.ensemble import (BaggingClassifier, BaggingRegressor, HistGradientBoostingClassifier,
                                  HistGradientBoostingRegressor, RandomForestClassifier, RandomForestRegressor)
    from sklearn.impute import SimpleImputer
    from sklearn.inspection import permutation_importance
    from sklearn.linear_model import LogisticRegression, RidgeCV
    from sklearn.model_selection import KFold, StratifiedKFold, cross_validate, train_test_split
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
except ImportError:
    sys.exit("needs numpy, pandas and scikit-learn: pip install numpy pandas scikit-learn")


def models(classify, seed=0):
    if classify:
        return {
            "logistic (baseline)": make_pipeline(SimpleImputer(), StandardScaler(), LogisticRegression(max_iter=2000)),
            "tree depth 5": make_pipeline(SimpleImputer(), DecisionTreeClassifier(max_depth=5, random_state=seed)),
            "bagged trees": make_pipeline(SimpleImputer(), BaggingClassifier(DecisionTreeClassifier(), n_estimators=100, random_state=seed, n_jobs=-1)),
            "random forest": make_pipeline(SimpleImputer(), RandomForestClassifier(n_estimators=300, min_samples_leaf=2, random_state=seed, n_jobs=-1)),
            "gradient boosting": HistGradientBoostingClassifier(early_stopping=True, random_state=seed),
        }
    return {
        "ridge (baseline)": make_pipeline(SimpleImputer(), StandardScaler(), RidgeCV()),
        "tree depth 5": make_pipeline(SimpleImputer(), DecisionTreeRegressor(max_depth=5, random_state=seed)),
        "bagged trees": make_pipeline(SimpleImputer(), BaggingRegressor(DecisionTreeRegressor(), n_estimators=100, random_state=seed, n_jobs=-1)),
        "random forest": make_pipeline(SimpleImputer(), RandomForestRegressor(n_estimators=300, min_samples_leaf=2, random_state=seed, n_jobs=-1)),
        "gradient boosting": HistGradientBoostingRegressor(early_stopping=True, random_state=seed),
    }


def cv_score(model, X, y, classify, folds=5, seed=0):
    cv = StratifiedKFold(folds, shuffle=True, random_state=seed) if classify else KFold(folds, shuffle=True, random_state=seed)
    r = cross_validate(model, X, y, cv=cv, scoring="roc_auc" if classify else "r2", return_train_score=True)
    return {"cv_mean": r["test_score"].mean(), "cv_sd": r["test_score"].std(),
            "train": r["train_score"].mean(), "gap": r["train_score"].mean() - r["test_score"].mean()}


def importances(X, y, classify, seed=0):
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=seed, stratify=y if classify else None)
    rf = models(classify, seed)["random forest"].fit(Xtr, ytr)
    perm = permutation_importance(rf, Xte, yte, n_repeats=10, random_state=seed,
                                  scoring="roc_auc" if classify else "r2", n_jobs=-1)
    return pd.DataFrame({"impurity": rf[-1].feature_importances_, "permutation": perm.importances_mean},
                        index=X.columns).sort_values("permutation", ascending=False)


def selftest():
    Xa, y = make_classification(n_samples=1500, n_features=12, n_informative=5, n_redundant=0,
                                flip_y=0.05, random_state=3)
    X = pd.DataFrame(Xa, columns=[f"f{i}" for i in range(12)])
    tree = cv_score(DecisionTreeClassifier(random_state=0), X, y, True)["cv_mean"]
    bag_tree = cv_score(BaggingClassifier(DecisionTreeClassifier(), n_estimators=100, random_state=0, n_jobs=-1), X, y, True)["cv_mean"]
    logit = cv_score(LogisticRegression(max_iter=2000), X, y, True)["cv_mean"]
    bag_logit = cv_score(BaggingClassifier(LogisticRegression(max_iter=2000), n_estimators=100, random_state=0, n_jobs=-1), X, y, True)["cv_mean"]
    assert bag_tree - tree > 0.08, f"bagging rescues a high-variance tree ({tree:.3f} -> {bag_tree:.3f})"
    assert abs(bag_logit - logit) < 0.01, f"bagging barely moves a low-variance model ({logit:.3f} -> {bag_logit:.3f})"

    rng = np.random.default_rng(0)
    X2 = pd.DataFrame({"signal": rng.normal(size=2000), "binary_noise": rng.integers(0, 2, 2000),
                       "continuous_noise": rng.normal(size=2000)})
    y2 = (X2.signal + rng.normal(scale=1.0, size=2000) > 0).astype(int)
    imp = importances(X2, y2, True)
    assert imp.loc["continuous_noise", "impurity"] > 5 * imp.loc["binary_noise", "impurity"], \
        "impurity importance rewards a continuous column that is pure noise"
    assert abs(imp.loc["continuous_noise", "permutation"]) < 0.01, "permutation importance shows it is useless"
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--csv")
    ap.add_argument("--target")
    ap.add_argument("--folds", type=int, default=5)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not (a.csv and a.target):
        ap.error("--csv and --target are required")
    df = pd.read_csv(a.csv).dropna(subset=[a.target])
    y = df.pop(a.target)
    X = pd.get_dummies(df, dummy_na=False).astype(float)
    classify = y.nunique() == 2
    if not classify and not pd.api.types.is_numeric_dtype(y):
        ap.error("target must be binary or numeric")
    if classify:
        y = (y == sorted(y.unique())[-1]).astype(int)
    rows = {name: cv_score(m, X, y, classify, a.folds) for name, m in models(classify).items()}
    metric = "ROC-AUC" if classify else "R-squared"
    print(f"{len(X):,} rows, {X.shape[1]} features, {a.folds}-fold CV, metric {metric}\n")
    print(pd.DataFrame(rows).T.round(3).to_string())
    print("\nRandom forest importance: impurity (training data) vs permutation (held-out data)\n")
    print(importances(X, y, classify).head(15).round(4).to_string())


if __name__ == "__main__":
    main()
