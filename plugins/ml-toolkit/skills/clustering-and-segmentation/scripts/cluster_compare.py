#!/usr/bin/env python3
"""Compare clustering methods and cluster counts on a table of numbers.

Scales the chosen columns, then reports for each k: k-means inertia,
silhouette and Calinski-Harabasz, agglomerative Ward silhouette, and Gaussian
mixture BIC. DBSCAN is tried at multiples of the knee of the k-distance curve,
reporting clusters found and the share of points left as noise. --profile
describes one solution: segment sizes, medians, and ANOVA F-score per feature.

  python3 cluster_compare.py --csv customers.csv --columns recency frequency spend --log spend
  python3 cluster_compare.py --csv customers.csv --profile kmeans:4
  python3 cluster_compare.py --selftest
Needs numpy, pandas and scikit-learn.
"""
import argparse
import sys

try:
    import numpy as np
    import pandas as pd
    from sklearn.cluster import DBSCAN, AgglomerativeClustering, KMeans
    from sklearn.feature_selection import f_classif
    from sklearn.metrics import adjusted_rand_score, calinski_harabasz_score, silhouette_score
    from sklearn.mixture import GaussianMixture
    from sklearn.neighbors import NearestNeighbors
    from sklearn.preprocessing import StandardScaler
except ImportError:
    sys.exit("needs numpy, pandas and scikit-learn: pip install numpy pandas scikit-learn")

SEED = 0
WARD_MAX_ROWS = 20_000


def silhouette(X, labels, sample=5000):
    keep = labels != -1
    if len(set(labels[keep])) < 2:
        return float("nan")
    return float(silhouette_score(X[keep], labels[keep], sample_size=min(sample, int(keep.sum())), random_state=SEED))


def fit(method, X, k=None, eps=None, min_samples=5):
    if method == "kmeans":
        return KMeans(k, n_init=10, random_state=SEED).fit_predict(X)
    if method == "ward":
        return AgglomerativeClustering(k, linkage="ward").fit_predict(X)
    if method == "gmm":
        return GaussianMixture(k, n_init=3, random_state=SEED).fit(X).predict(X)
    if method == "dbscan":
        return DBSCAN(eps=eps, min_samples=min_samples).fit_predict(X)
    raise SystemExit(f"unknown method {method}; use kmeans, ward, gmm")


def compare(X, ks):
    rows = []
    for k in ks:
        km = KMeans(k, n_init=10, random_state=SEED).fit(X)
        ward = fit("ward", X, k) if len(X) <= WARD_MAX_ROWS else None
        rows.append({
            "k": k,
            "kmeans_inertia": round(km.inertia_, 1),
            "kmeans_silhouette": round(silhouette(X, km.labels_), 3),
            "kmeans_ch": round(calinski_harabasz_score(X, km.labels_), 1),
            "ward_silhouette": round(silhouette(X, ward), 3) if ward is not None else float("nan"),
            "gmm_bic": round(GaussianMixture(k, n_init=3, random_state=SEED).fit(X).bic(X), 1),
        })
    return pd.DataFrame(rows)


def knee(values):
    """Point on a sorted curve farthest from the straight line joining its ends."""
    x = np.linspace(0, 1, len(values))
    span = values[-1] - values[0]
    y = (values - values[0]) / span if span else np.zeros_like(values)
    return float(values[int(np.argmax(x - y))])


def dbscan_scan(X, min_samples=None):
    min_samples = min_samples or max(5, 2 * X.shape[1])
    dist = np.sort(NearestNeighbors(n_neighbors=min_samples).fit(X).kneighbors(X)[0][:, -1])
    base = knee(dist)
    rows = []
    for mult in (0.5, 0.75, 1.0, 1.5, 2.0):
        eps = base * mult
        labels = fit("dbscan", X, eps=eps, min_samples=min_samples)
        rows.append({"eps_x_knee": mult, "eps": round(eps, 3), "min_samples": min_samples,
                     "clusters": len(set(labels) - {-1}),
                     "noise_pct": round(float((labels == -1).mean() * 100), 1),
                     "silhouette_non_noise": round(silhouette(X, labels), 3)})
    return pd.DataFrame(rows)


def profile(raw, X, spec):
    method, k = spec.split(":")
    labels = fit(method, X, int(k))
    F, _ = f_classif(X, labels)
    sizes = pd.Series(labels).value_counts(normalize=True).sort_index().mul(100).round(1)
    medians = raw.groupby(labels).median().round(2)
    medians.insert(0, "share_pct", sizes)
    print(f"\nSegments ({spec}): size and medians on the original scale")
    print(medians.to_string())
    print("\nFeatures ranked by how strongly they separate segments (ANOVA F)")
    print(pd.Series(F, index=raw.columns).sort_values(ascending=False).round(1).to_string())


def load(path, columns, log_cols):
    df = pd.read_csv(path)
    raw = df[columns] if columns else df.select_dtypes("number")
    before = len(raw)
    raw = raw.dropna()
    if len(raw) < before:
        print(f"dropped {before - len(raw)} rows with missing values")
    X = raw.copy()
    for c in log_cols or []:
        if (X[c] < 0).any():
            raise SystemExit(f"cannot log-transform {c}: it has negative values")
        X[c] = np.log1p(X[c])
    return raw, StandardScaler().fit_transform(X)


def selftest():
    from sklearn.datasets import make_blobs, make_circles
    X, _ = make_blobs(600, centers=[[0, 0], [6, 0], [0, 6], [6, 6]], cluster_std=0.8, random_state=1)
    t = compare(StandardScaler().fit_transform(X), range(2, 8))
    assert int(t.loc[t.kmeans_silhouette.idxmax(), "k"]) == 4, "silhouette should pick 4 blobs"
    assert int(t.loc[t.kmeans_ch.idxmax(), "k"]) == 4, "Calinski-Harabasz should pick 4 blobs"
    Xc, yc = make_circles(600, factor=0.4, noise=0.04, random_state=1)
    Xc = StandardScaler().fit_transform(Xc)
    assert adjusted_rand_score(yc, fit("kmeans", Xc, 2)) < 0.2, "k-means cannot separate rings"
    scan = dbscan_scan(Xc, min_samples=5)
    best = max(adjusted_rand_score(yc, fit("dbscan", Xc, eps=e, min_samples=5)) for e in scan.eps)
    assert best > 0.9, "DBSCAN with an eps from the k-distance scan should separate rings"
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--csv")
    ap.add_argument("--columns", nargs="*")
    ap.add_argument("--log", nargs="*", help="columns to log1p-transform before scaling")
    ap.add_argument("--k-min", type=int, default=2)
    ap.add_argument("--k-max", type=int, default=8)
    ap.add_argument("--profile", help="method:k, e.g. kmeans:4")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.csv:
        ap.error("--csv is required")
    raw, X = load(a.csv, a.columns, a.log)
    if a.profile:
        return profile(raw, X, a.profile)
    t = compare(X, range(a.k_min, a.k_max + 1))
    print("By cluster count (silhouette and CH: higher is better; BIC: lower is better)")
    print(t.to_string(index=False))
    print(f"\nbest k: silhouette {int(t.loc[t.kmeans_silhouette.idxmax(), 'k'])}, "
          f"CH {int(t.loc[t.kmeans_ch.idxmax(), 'k'])}, GMM BIC {int(t.loc[t.gmm_bic.idxmin(), 'k'])}")
    print("\nDBSCAN at multiples of the k-distance knee")
    print(dbscan_scan(X).to_string(index=False))


if __name__ == "__main__":
    main()
