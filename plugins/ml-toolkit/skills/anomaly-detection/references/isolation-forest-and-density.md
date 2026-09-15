# Isolation forest, local outlier factor and density methods

## Isolation forest

**Idea:** anomalies are few and different, so random splits isolate them quickly.
1. Build a tree by picking a random feature and a random split value, repeatedly, until each point sits alone.
2. Record how many splits it took to isolate each point: its path length.
3. Build many such trees on random subsamples and average the path lengths. One tree is fragile; the average is stable.
4. Short average paths mean anomalies. The score is scaled so values near 1 are likely anomalies and values well below 0.5 are normal.

**Settings:** `n_estimators` 100–300; `max_samples` 256 by default, which works surprisingly well; `contamination` only sets where `predict` draws the line, so rank by `score_samples` and cut at the team's capacity instead. Scale features and log-transform skewed ones.

**Strengths:** fast on large, high-dimensional data; no distribution assumption; needs no labels.
**Limits:** splits are axis-parallel, so anomalies that break a correlation between features are found less reliably than by Mahalanobis distance; scores are hard to explain without looking at per-feature deviations.

## Local outlier factor (LOF)

Compares each point's local density with its neighbours' density. A point in a sparse pocket next to a dense cluster gets a high LOF, even if a sparse cluster elsewhere is normal.
- `n_neighbors` 20–50 is a common start.
- Handles clusters of different density better than global methods.
- Slower on large data; use `novelty=True` to score new records.

## Density estimation

Fit a density model to normal data (kernel density, or a Gaussian mixture) and flag records in low-density regions. The kernel bandwidth controls smoothness: too small and every new point looks unusual, too large and anomalies blend in. Works best with few features.

## DBSCAN noise points

Points that belong to no dense cluster are labelled noise. Useful as a by-product of clustering, but `eps` is tuned for clusters, not for anomaly precision.

## Moving to supervised learning

Once reviewers have labelled enough alerts across the kinds of problem that matter, train a classifier on them and keep an unsupervised detector running for new patterns the classifier has never seen.
