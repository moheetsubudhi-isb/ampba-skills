#!/usr/bin/env python3
"""Score records by univariate z-score, Mahalanobis distance and isolation forest.

Uses the numeric columns (or those named). Prints how many of each method's
top-k records the others also flag, then the top-k by isolation forest with
the features that deviate most for each record. Use --top to set k to the
team's review capacity.

  python3 anomaly_compare.py --csv transactions.csv --columns amount hour km_from_home --top 50 --log amount
  python3 anomaly_compare.py --selftest
Needs numpy, pandas and scikit-learn.
"""
import argparse
import sys

try:
    import numpy as np
    import pandas as pd
    from sklearn.covariance import MinCovDet
    from sklearn.ensemble import IsolationForest
except ImportError:
    sys.exit("needs numpy, pandas and scikit-learn: pip install numpy pandas scikit-learn")


def scores(X, seed=0):
    z = (X - X.median()) / (X.quantile(0.75) - X.quantile(0.25)).replace(0, 1) * 1.349
    mcd = MinCovDet(random_state=seed).fit(X)
    iso = IsolationForest(n_estimators=300, random_state=seed).fit(X)
    return pd.DataFrame({"max_abs_z": z.abs().max(axis=1),
                         "mahalanobis": np.sqrt(mcd.mahalanobis(X)),
                         "isolation_forest": -iso.score_samples(X)}, index=X.index), z


def top(s, k):
    return set(s.nlargest(k).index)


def selftest():
    rng = np.random.default_rng(0)
    n = 3000
    normal = rng.multivariate_normal([0, 0], [[1, 0.95], [0.95, 1]], size=n)
    odd = np.array([[2.0, -2.0], [-2.0, 2.0], [1.8, -1.8], [-1.9, 1.9], [2.1, -2.0]])
    X = pd.DataFrame(np.vstack([normal, odd]), columns=["income", "spend"])
    planted = set(range(n, n + 5))
    s, z = scores(X)
    assert z.loc[list(planted)].abs().max(axis=1).max() < 3, "each value alone looks ordinary"
    assert planted <= top(s.mahalanobis, 10), "Mahalanobis catches combinations that break the correlation"
    assert len(planted & top(s.max_abs_z, 10)) == 0, "univariate z-scores miss them entirely"
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--csv")
    ap.add_argument("--columns", nargs="+")
    ap.add_argument("--log", nargs="*", default=[], help="columns to log1p-transform first")
    ap.add_argument("--top", type=int, default=50)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.csv:
        ap.error("--csv is required")
    df = pd.read_csv(a.csv)
    X = (df[a.columns] if a.columns else df.select_dtypes("number")).dropna()
    for c in a.log:
        X[c] = np.log1p(X[c].clip(lower=0))
    s, z = scores(X)
    k = min(a.top, len(X))
    sets = {m: top(s[m], k) for m in s.columns}
    print(f"{len(X):,} records, {X.shape[1]} features, top {k} per method\n")
    print(pd.DataFrame({m: {o: len(sets[m] & sets[o]) for o in sets} for m in sets}).to_string())
    print("\n(overlap counts: a low number between z-score and the others means the anomalies are combinations)\n")
    best = s.isolation_forest.nlargest(k).index
    reasons = z.loc[best].abs().apply(lambda r: ", ".join(f"{c} {z.loc[r.name, c]:+.1f}" for c in r.nlargest(2).index), axis=1)
    out = df.loc[best, X.columns].assign(**s.loc[best].round(3), why=reasons)
    print(out.to_string())


if __name__ == "__main__":
    main()
