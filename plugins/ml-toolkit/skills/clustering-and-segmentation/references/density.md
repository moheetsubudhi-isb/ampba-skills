# DBSCAN and HDBSCAN

**Use when** clusters have irregular shapes, outliers should stay unassigned, or the number of clusters is unknown.

**How it works**
- `eps` is the neighbourhood radius.
- `min_samples` is the number of neighbours within `eps` needed to make a point a core point.
- Core points connected through their neighbourhoods form a cluster. Border points attach to a nearby core point. Everything else is noise, labelled −1.

**Procedure**
1. Scale the columns. This is mandatory, because `eps` is a single distance applied to every column.
2. Set `min_samples` to about twice the number of features, with a minimum of 5.
3. Plot each point's distance to its `min_samples`-th neighbour, sorted. Take `eps` near the knee of that curve, where distances start rising steeply. `scripts/cluster_compare.py` finds the knee and tries 0.5× to 2× its value. Read quantiles with care: on dense data every percentile can sit below the knee and split real clusters into fragments.
4. Read the share of noise.
   - Under 5%: clean structure.
   - 5–20%: normal for real data.
   - Over 30%: `eps` is too small, or the data has no dense structure.
5. When clusters have very different densities, use HDBSCAN (`sklearn.cluster.HDBSCAN`). It adapts to local density and needs only `min_cluster_size`.

**Reading the result**
Silhouette is a poor judge of density clustering: it rewards round, well-separated clusters. A DBSCAN solution that recovers two concentric rings perfectly can score about 0.15. Judge by the share of noise, the number of clusters found, and whether the shapes make business sense.

**Limits**
One `eps` cannot fit clusters of very different densities; HDBSCAN handles that. Distances weaken in high dimensions, so reduce dimensions first. Noise points need a business decision: ignore them, review them, or assign each to its nearest cluster.
