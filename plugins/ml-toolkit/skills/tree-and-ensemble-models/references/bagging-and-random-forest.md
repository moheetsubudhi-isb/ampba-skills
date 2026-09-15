# Bagging and random forests

## Bagging (bootstrap aggregation)

1. Draw a bootstrap sample: n rows sampled with replacement from n rows.
2. Fit a model on it.
3. Repeat many times, then combine: majority vote for classes, average for numbers.

**Why it helps:** averaging many unstable models cancels much of their variance. It helps high-variance models such as deep trees and flexible SVMs a lot, and low-variance models such as logistic regression barely at all.

**Out-of-bag (OOB) rows:** the chance a row is never drawn in n picks is (1 − 1/n)ⁿ ≈ e⁻¹ ≈ 37%. Each model can be scored on the rows it never saw, and the combined OOB score is a nearly free estimate of accuracy on new data, often good enough to replace cross-validation for tuning.

## Random forest

Bagged trees plus one change: at each split, each tree considers only a random subset of features. That decorrelates the trees, so averaging removes more variance than plain bagging.

**Settings that matter**
- `max_features`: features tried per split. Common defaults: √p for classification, p/3 to p for regression. Lower values give more diverse trees.
- `min_samples_leaf` and `max_depth`: control how closely each tree fits.
- `n_estimators`: more trees stabilise results and rarely hurt; pick enough that the OOB score stops moving (often 300–1,000), then stop tuning it.
- `class_weight` or balanced sampling for rare classes.

**Feature importance**
- Built-in importance is the total impurity decrease from splits on each feature, averaged over trees. It is biased toward continuous and high-cardinality features, and computed on training data.
- Permutation importance shuffles one feature in held-out data and measures how much the score drops. Slower, but honest about what matters on new data.
- Correlated features share credit under both methods.

**Strengths:** strong accuracy with little tuning, robust to outliers and noisy features, handles interactions and non-linearity, parallel training.
**Limits:** large models, slower scoring than a single tree, hard to read, cannot extrapolate beyond the training range.
