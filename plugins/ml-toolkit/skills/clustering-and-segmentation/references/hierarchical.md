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
