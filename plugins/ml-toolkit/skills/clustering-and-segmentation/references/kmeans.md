# k-means

**Use when** the columns are numeric and scaled, groups are roughly round and similar in size, and there is a rough idea of how many groups exist.

**Procedure**
1. Scale the columns. Log-transform heavy-tailed ones first.
2. Fit with k-means++ initialisation and `n_init` of at least 10, for k from 2 to about 10.
3. Plot inertia against k to find the elbow. Plot silhouette and Calinski-Harabasz against k.
4. Pick k where the metrics agree, or the actionable k closest to their peak.
5. Refit with the chosen k and a fixed seed. Check stability across seeds and subsamples using the adjusted Rand index.

**Limits**
- It assumes round clusters of similar size. It splits elongated shapes and merges small groups.
- k must be chosen in advance.
- Outliers pull centroids away from where they belong. Remove or cap outliers, or use k-medoids.
- It degrades in high dimensions. Reduce dimensions first.

**Scale**
Use `MiniBatchKMeans` above roughly a million rows. Compute silhouette on a sample.
