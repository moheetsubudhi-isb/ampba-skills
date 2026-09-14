#!/usr/bin/env python3
"""Show what PCA keeps, and whether it throws away class signal compared to LDA.

  python3 projection_check.py --csv sensors.csv
  python3 projection_check.py --csv sensors.csv --target failed --dims 2
  python3 projection_check.py --selftest
Needs numpy, pandas and scikit-learn.
"""
import argparse
import sys

try:
    import numpy as np
    import pandas as pd
    from sklearn.decomposition import PCA
    from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import StratifiedKFold, cross_val_score
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
except ImportError:
    sys.exit("needs numpy, pandas and scikit-learn: pip install numpy pandas scikit-learn")


def variance_report(X, names):
    pca = PCA().fit(StandardScaler().fit_transform(X))
    ratio = pca.explained_variance_ratio_
    cum = np.cumsum(ratio)
    need = {t: int(np.searchsorted(cum, t) + 1) for t in (0.8, 0.9, 0.95)}
    loadings = []
    for i, comp in enumerate(pca.components_[:3]):
        top = np.argsort(-np.abs(comp))[:3]
        loadings.append(f"PC{i + 1} ({ratio[i]:.1%}): " + ", ".join(f"{names[j]} {comp[j]:+.2f}" for j in top))
    return ratio, need, loadings


def separation(X, y, dims):
    cv = StratifiedKFold(5, shuffle=True, random_state=0)
    lda_dims = min(dims, len(np.unique(y)) - 1)
    score = lambda reducer: cross_val_score(
        make_pipeline(StandardScaler(), reducer, LogisticRegression(max_iter=1000)), X, y, cv=cv).mean()
    return score(PCA(dims)), score(LinearDiscriminantAnalysis(n_components=lda_dims)), lda_dims


def selftest():
    rng = np.random.default_rng(0)
    n = 800
    y = rng.integers(0, 2, n)
    shared = rng.normal(0, 1, n)
    noise_block = np.column_stack([shared + rng.normal(0, 0.2, n) for _ in range(5)])
    signal = y + rng.normal(0, 0.35, n)
    X = np.column_stack([noise_block, signal])
    ratio, need, _ = variance_report(X, [f"f{i}" for i in range(6)])
    assert ratio[0] > 0.6, "correlated block should dominate PC1"
    pca_acc, lda_acc, _ = separation(X, y, 1)
    assert lda_acc - pca_acc > 0.3, f"PCA should lose the class signal (PCA {pca_acc:.2f}, LDA {lda_acc:.2f})"
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--csv")
    ap.add_argument("--columns", nargs="*")
    ap.add_argument("--target")
    ap.add_argument("--dims", type=int, default=2)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.csv:
        ap.error("--csv is required")
    df = pd.read_csv(a.csv)
    feats = df[a.columns] if a.columns else df.drop(columns=[a.target] if a.target else []).select_dtypes("number")
    data = pd.concat([feats, df[a.target]], axis=1).dropna() if a.target else feats.dropna()
    X = data[feats.columns].to_numpy()
    ratio, need, loadings = variance_report(X, list(feats.columns))
    print(f"{X.shape[1]} numeric features, {len(X)} complete rows")
    print("components needed for 80% / 90% / 95% of variance:", need[0.8], need[0.9], need[0.95])
    print("\n".join(loadings))
    if a.target:
        pca_acc, lda_acc, lda_dims = separation(X, data[a.target].to_numpy(), a.dims)
        print(f"\n5-fold accuracy with logistic regression: PCA({a.dims}) {pca_acc:.3f} vs LDA({lda_dims}) {lda_acc:.3f}")
        if lda_acc - pca_acc > 0.05:
            print("PCA discards class signal here; prefer LDA or feature selection for this task.")


if __name__ == "__main__":
    main()
