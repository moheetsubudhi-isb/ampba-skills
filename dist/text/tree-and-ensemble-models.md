# tree-and-ensemble-models

Use this skill when: Build, tune and explain decision trees and tree ensembles: random forest, bagging, AdaBoost, gradient boosting, XGBoost, LightGBM and CatBoost. Use whenever someone asks whether to use a single tree, a random forest or boosting; how to set max_depth, min_samples_leaf, n_estimators, learning rate, max_features or subsample for one of these models; gini or entropy; how to prune a tree; why a tree overfits or a boosted model is unstable; what the out-of-bag score means; how far to trust feature importance, or when to use permutation importance or SHAP instead; how to turn a tree into business rules; or whether a regression tree beats linear regression. Not for designing the validation split or reading bias-variance in general, and not for choosing a classification threshold.

# Tree and ensemble models

Act as the data scientist who picks and tunes the tree model, and as the advisor who explains what drives its predictions without claiming more than the model can show.

## Get the context that changes the answer

If data, code or a fitted model is available, look at it first: rows, features, class balance, current hyperparameters, and training versus validation scores.

Then ask only what that material cannot answer, and only if the answer would change the model. Ask at most three questions. Give each one a one-line reason and a default. If the request is urgent, give a first model on stated assumptions and list the questions that would sharpen it.

The questions that usually matter here:

1. **Does anyone need to read the model itself, or only use its predictions?** A shallow tree can be printed as rules; an ensemble needs explanation tools.
2. **How much data, how many features, and how fast must scoring be?** This decides between a forest and boosting, and how much tuning is affordable.
3. **What will the feature importance be used for?** Choosing what to monitor is fine. Claiming a feature causes the outcome is not.

If there is no answer, assume predictions matter more than readability, tabular data under a few million rows, gradient boosting as the first candidate, and permutation importance for explanation.

## Procedure

Where a step names a script and code cannot run here, do the same check by hand on a small case, and say in the deliverable that it was done by hand.

1. **Set baselines first:** a regularised linear or logistic model and a shallow tree. An ensemble must beat both on validation data to earn its complexity.
2. **Pick the family**, then load its reference.

   | Need | Model | Load |
   |---|---|---|
   | Rules people can read, audit or put in a policy | Single tree, depth 3–5, pruned | `references/single-tree.md` |
   | Strong default with little tuning; robust to noise | Random forest | `references/bagging-and-random-forest.md` |
   | Highest accuracy on tabular data, with time to tune | Gradient boosting (XGBoost, LightGBM, CatBoost) | `references/boosting.md` |
   | Any unstable, high-variance base model | Bagging | `references/bagging-and-random-forest.md` |

3. **Split before anything learns from the data.** Fit imputation, encoding and outlier rules inside the training folds, in a pipeline. Trees need no feature scaling.
4. **Tune the few settings that matter**, listed in each reference. Use cross-validation, or the out-of-bag score for forests, and early stopping on a validation set for boosting.
5. **Compare candidates** with `scripts/ensemble_compare.py`. It reports cross-validated scores for a linear baseline, a tree, bagging, a random forest and gradient boosting, each with its training-validation gap, and puts impurity importance beside permutation importance.
6. **Explain honestly.**
   - Impurity-based importance favours continuous and high-cardinality features, even pure noise. Prefer permutation importance on held-out data, or SHAP values.
   - Correlated features split their importance, so each looks weaker than the pair.
   - Importance shows what the model uses, not what causes the outcome.
7. **Check stability.** Refit with different seeds and folds. If the score or the top features move a lot, report the range, not one number.

## Deliverable

**Part A: Model brief**, for the decision owner

- The recommended model and its gain over the baseline, in business terms.
- The main drivers of its predictions, described as associations.
- Whether a simpler model is nearly as good, and what would make this one fail, such as drift in a top feature.

**Part B: Technical appendix**, for the builders

- Hyperparameters and the search that chose them.
- Cross-validated scores with their spread, and the training-validation gap.
- Importance from both methods; the rules, if it is a single tree; the code.

## Traps

- Scoring ROC-AUC on predicted labels instead of predicted probabilities.
- Removing outliers or encoding categories on the full dataset before splitting.
- Trusting default impurity importance, especially next to ID-like or continuous noise columns.
- Calling a 15-level tree interpretable.
- Boosting for thousands of rounds with no early stopping.
- Bagging a stable model such as logistic regression and expecting a gain.
- Grid-searching the number of trees in a random forest: more trees rarely hurt. Tune depth, leaf size and max_features instead.

---

## Reference: references/bagging-and-random-forest.md

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

---

## Reference: references/boosting.md

# Boosting

Boosting builds models one after another, each correcting the errors of those before it. Bagging builds models independently and gives each an equal vote; boosting builds them in sequence and weights them.

## AdaBoost

1. Give every row an equal weight.
2. Fit a weak learner, usually a one-split tree (a stump).
3. Compute its weighted error ε, and its say α = ½ ln((1 − ε)/ε). Lower error means more say.
4. Increase the weights of misclassified rows and decrease the rest, then normalise.
5. Repeat; the final prediction is the class with the largest total say.

Sensitive to noisy labels and outliers, because misclassified rows keep gaining weight.

## Gradient boosting

1. Start from a constant prediction, such as the mean.
2. Compute residuals: more generally, the negative gradient of the loss for each row.
3. Fit a small tree to the residuals.
4. Add the tree's predictions, scaled by the learning rate, to the running prediction.
5. Repeat until validation error stops improving.

**XGBoost, LightGBM and CatBoost** add regularisation on leaf values and tree size, second-order gradients, fast histogram-based splits, native handling of missing values, and, in CatBoost, careful encoding of categorical features. XGBoost keeps a split only if its gain exceeds a threshold (γ).

## Settings that matter

- `learning_rate` with `n_estimators`: a lower rate needs more trees and usually generalises better. Set a low rate (0.03–0.1), a high tree limit, and **early stopping** on a validation set.
- Tree size: `max_depth` 3–8, or `num_leaves` in LightGBM; `min_child_weight` or `min_data_in_leaf`.
- Randomness: `subsample` (rows) and `colsample_bytree` (features), often 0.6–0.9.
- Regularisation: `lambda` (L2) and `alpha` (L1) on leaf weights.
- Imbalance: `scale_pos_weight`, or class weights, and judge by a cost-based metric.

## Strengths and limits

- Usually the most accurate choice for tabular data.
- Overfits if rounds run on without early stopping; more settings to tune; sequential training.
- Explain with permutation importance or SHAP rather than built-in gain importance.

---

## Reference: references/single-tree.md

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
