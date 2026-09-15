# Single decision trees

**How a tree grows:** at each node it tries every feature and every split value, and keeps the split that makes the child nodes purest. It is greedy: it never revisits an earlier split, so it can miss a better tree overall.

**Purity measures (classification)**
- **Gini impurity** = Σ pᵢ(1 − pᵢ) over classes. Zero for a pure node. Slightly faster; tends to isolate the most frequent class in its own branch.
- **Entropy** = −Σ pᵢ log₂ pᵢ. Zero for a pure node. Tends to give more balanced trees.
- The two usually give very similar trees; do not spend tuning time choosing between them.

**Regression trees** choose the split that minimises the sum of squared errors, and predict the mean of the target in each leaf. They capture non-linear effects and interactions and handle mixed feature types without assumptions such as constant error variance, but predictions are step-shaped and cannot extrapolate beyond the training range.

**Controlling complexity**
- `max_depth`: 3–5 for readable rules; deeper only inside ensembles.
- `min_samples_leaf`: a leaf must hold enough rows to be trusted, often 1–5% of the data for a policy tree.
- `min_samples_split`, `max_leaf_nodes`, and a minimum impurity decrease.

**Pruning:** grow a large tree, then remove branches whose improvement does not justify their size. Cost-complexity pruning minimises error + α × (number of leaves). Find the path of α values with `cost_complexity_pruning_path`, then choose α by cross-validation.

**Turning a tree into rules:** each path from root to leaf is a rule, such as "tenure < 6 months AND support tickets ≥ 3 → churn risk 42% (n = 310)". Always show the number of rows and the class share in each leaf.

**Limits:** high variance: small changes in data can change the whole tree. Accuracy on new data is usually lower than an ensemble's. Use a single tree when readability is the requirement, and check that its accuracy is close enough to the ensemble to accept the trade.
