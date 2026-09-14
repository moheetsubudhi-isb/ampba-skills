# clustering-and-segmentation

Use this skill when: Group customers, products, stores, sessions or any records into segments, and pick the clustering method that fits the data and the business use. Use whenever someone wants to segment, cluster or group similar items, build personas or cohorts from behaviour, run k-means, hierarchical clustering, DBSCAN or Gaussian mixtures, choose the number of clusters, read an elbow plot, silhouette score or Calinski-Harabasz index, profile or name clusters, build an RFM segmentation, cluster mixed categorical and numeric data, or check whether segments someone else built are real. Not for reducing the number of columns before modelling, and not for predicting a label that already exists.

# Clustering and segmentation

Act as the data scientist who builds the segments and as the advisor who makes sure a team can act on them. A segment is only worth having if someone treats it differently.

## Get the context that changes the answer

If data is available, look at it first. Answer what you can from the data itself: row count, column types, skew, missing values.

Then ask only what the data and the request cannot answer, and only if the answer would change the method or the output. Ask at most three questions. Give each one a one-line reason and a default, such as "If you're not sure, I'll assume campaign targeting." If the request is exploratory or urgent, deliver a first cut on stated assumptions and list the questions that would sharpen it.

The questions that usually matter here:

1. **What will the segments be used for?** Campaign targeting needs a few stable, easy-to-explain groups. Store or product operations can use more groups. Exploring for unusual behaviour needs a method that can leave points unassigned. The answer picks the method before any data is touched.
2. **How many segments can the team actually act on?** Usually three to seven. This number breaks ties that the metrics cannot.
3. **Which columns describe behaviour, and are any off limits?** Leave sensitive attributes such as gender, religion or caste out, unless there is a clear and lawful reason to include them.

## Procedure

Where a step names a script and code cannot run here, do the same check by hand on a small case, and say in the deliverable that it was done by hand.

1. **Prepare the features.**
   - Keep the behavioural columns that relate to the use case.
   - Log-transform heavy-tailed columns such as spend or order counts.
   - Scale everything. Otherwise the column with the largest range decides the distances.
   - Encode categories carefully. For mixed data, load `references/mixed-types.md`.
   - With more than about 20 features, remove near-duplicate columns or reduce dimensions first. Distances lose meaning as dimensions grow.
2. **Choose the distance.**
   - **Euclidean:** when magnitude matters.
   - **Cosine:** when the pattern matters more than the volume — for example, two customers with the same category mix but very different spend.
   - **Jaccard:** for sets such as baskets or feature flags.
3. **Choose the method, then load its reference.**

   | Data and goal | Method | Load |
   |---|---|---|
   | Roughly round, similar-sized groups; numeric; a rough idea of how many | k-means | `references/kmeans.md` |
   | Want a hierarchy, small to medium data, or no idea how many groups | Agglomerative clustering with a dendrogram | `references/hierarchical.md` |
   | Irregular shapes, outliers that should stay unassigned, uneven density | DBSCAN or HDBSCAN | `references/density.md` |
   | Overlapping groups, or a need for membership probabilities | Gaussian mixture | `references/gmm.md` |
   | A mix of categorical and numeric columns | Gower distance or k-prototypes | `references/mixed-types.md` |

4. **Compare solutions on the data.** Run `scripts/cluster_compare.py`. It scales the columns, then reports across a range of k:
   - k-means inertia (for the elbow), silhouette and Calinski-Harabasz;
   - Ward silhouette;
   - Gaussian mixture BIC;
   - DBSCAN results across several `eps` values, including the share of points left as noise.
5. **Choose k, reading the metrics together.**
   - **Silhouette** runs from −1 to 1. Rough guide: above 0.7 is strong structure, 0.5–0.7 reasonable, 0.25–0.5 weak, below 0.25 no real structure.
   - **Calinski-Harabasz** is relative. Use it only to compare solutions on the same data.
   - **The elbow** is where adding a cluster stops reducing within-cluster spread much.
   - When the metrics disagree or sit close together, the number of segments the team can act on decides.
6. **Check stability.** Re-run with different seeds and on 80% samples, and compare assignments with the adjusted Rand index. Segments that reshuffle between runs will not survive next month's refresh.
7. **Profile and name the segments.**
   - Give each segment's size, and each feature's median on its original scale.
   - Rank features by ANOVA F-score: `python3 scripts/cluster_compare.py --csv data.csv --profile kmeans:4`.
   - Name each segment by its two or three defining traits, in business language — for example, "Lapsed high spenders".
8. **Advise.**
   - Is every segment large enough to act on?
   - Does each segment get a different action?
   - Would a simple rule, such as "top 10% by spend", produce the same groups? If so, recommend the rule. It is cheaper and easier to explain.

## Deliverable

**Part A: Segment brief**

- A segment table with columns: name · share of records · defining traits · suggested action.
- The method used, and why it fits this data and use.
- Quality: silhouette, and stability measured by the adjusted Rand index.
- Caveats, and how often to refresh the segments.

**Part B: Technical appendix**

- Features and transforms.
- Method and parameters.
- The metric table across k.
- Seed and code, so the result can be reproduced.

## Traps

- Unscaled features, so spend in rupees decides everything.
- k-means on elongated or very uneven clusters.
- A high silhouette that comes from one tiny outlier cluster.
- Judging a density solution by silhouette. Silhouette rewards round, separated clusters, so a correct DBSCAN result on ring or crescent shapes can score near 0.15 while matching the truth exactly. For density methods, judge by the share of noise and by whether the shapes mean something to the business.
- Chasing the metric over what the team can act on.
- Clustering on ID numbers or postcodes treated as quantities.
- Training a classifier on cluster labels and then "validating" it against the same labels. That is circular.
- Sensitive attributes in the features without a clear, lawful reason.

---

## Reference: references/density.md

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

---

## Reference: references/gmm.md

# Gaussian mixture models

**Use when** groups overlap, clusters are elliptical rather than round, or the business needs membership probabilities — for example, "70% likely to be a bargain hunter".

**Procedure**
1. Scale the columns.
2. Fit k from 1 to about 10 with `n_init` of at least 3. Choose k by the lowest BIC.
3. Choose the covariance type:
   - `full`: flexible ellipses, many parameters;
   - `diag`: axis-aligned ellipses;
   - `spherical`: behaves like k-means.
   Compare BIC across types.
4. Use `predict_proba` for soft membership. Flag records with no component above about 0.6 as mixed.

**Limits**
Sensitive to initialisation, so use several starts. With too few rows per component, full covariance overfits. It assumes each group is roughly Gaussian, so log-transform skewed columns first.

---

## Reference: references/hierarchical.md

# Hierarchical clustering

**Use when** a hierarchy is useful (segments within segments), the number of groups is unknown, or the data has fewer than about 20,000 rows.

**Types**
- **Agglomerative (bottom-up):** every point starts as its own cluster, and the closest clusters merge step by step. This is the usual choice.
- **Divisive (top-down):** everything starts in one cluster, which is split recursively. Rarely available in libraries.

**Linkage** decides the distance between two clusters.

| Linkage | Behaviour | Use when |
|---|---|---|
| Ward | Merges the pair that increases within-cluster variance least; compact, even clusters | Numeric, Euclidean data — the default |
| Complete | Distance between the farthest points; compact clusters | Tight, similar-diameter groups |
| Average | Mean distance across all pairs; balanced | Non-Euclidean distances such as cosine |
| Single | Distance between the nearest points; forms chains | Elongated shapes; very sensitive to noise |

**Procedure**
1. Scale the columns and choose a distance. Ward requires Euclidean distance.
2. Build the linkage matrix and plot the dendrogram.
3. Cut where the vertical gaps are largest, or at the actionable k.
4. Check the cophenetic correlation. Above about 0.75, the tree reflects the original distances well.

**Limits**
Memory grows with the square of the row count, so sample large datasets. Merges cannot be undone, so an early bad merge persists.

---

## Reference: references/kmeans.md

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

---

## Reference: references/mixed-types.md

# Mixed categorical and numeric data

One-hot encoding followed by k-means is the common default, and usually a poor one. Dummy columns dominate the distances, and the centroids stop meaning anything.

**Options**
| Approach | How | Use when |
|---|---|---|
| Gower distance + agglomerative clustering or k-medoids | Gower scales each numeric column by its range and scores categories as match or mismatch, then averages | Small to medium data; interpretable |
| k-prototypes | k-means for numeric columns plus k-modes for categorical ones, with a weight between the two parts | Larger data; needs the `kmodes` package |
| Frequency or ordinal encoding + scaling | Replace each category with its share of rows, or its natural order | Categories carry a real order or a meaningful frequency |
| Cluster numeric columns, then profile by category | Keep categories out of the distance, and describe segments by them afterwards | Categories describe who, not how people behave |

**Checks**
- Weigh numeric and categorical contributions explicitly. Do not let whichever part has more columns win by default.
- High-cardinality categories, such as city with 4,000 values, should be grouped into broader levels first.
