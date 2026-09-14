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
