---
name: clustering-and-segmentation
description: >-
  Group customers, products, stores, sessions or any records into segments,
  and pick the clustering method that fits the data and the business use.
  Use whenever someone wants to segment, cluster or group similar items,
  build personas or cohorts from behaviour, run k-means, hierarchical
  clustering, DBSCAN or Gaussian mixtures, choose the number of clusters,
  read an elbow plot, silhouette score or Calinski-Harabasz index, profile or
  name clusters, build an RFM segmentation, cluster mixed categorical and
  numeric data, or check whether segments someone else built are real. Not
  for reducing the number of columns before modelling, and not for predicting
  a label that already exists.
---

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
