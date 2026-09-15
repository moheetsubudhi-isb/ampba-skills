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
