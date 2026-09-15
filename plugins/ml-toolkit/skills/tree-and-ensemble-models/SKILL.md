---
name: tree-and-ensemble-models
description: >-
  Build, tune and explain decision trees and tree ensembles: random forest,
  bagging, AdaBoost, gradient boosting, XGBoost, LightGBM and CatBoost. Use
  whenever someone asks whether to use a single tree, a random forest or
  boosting; how to set max_depth, min_samples_leaf, n_estimators, learning
  rate, max_features or subsample for one of these models; gini or entropy;
  how to prune a tree; why a tree overfits or a boosted model is unstable;
  what the out-of-bag score means; how far to trust feature importance, or
  when to use permutation importance or SHAP instead; how to turn a tree into
  business rules; or whether a regression tree beats linear regression. Not
  for designing the validation split or reading bias-variance in general, and
  not for choosing a classification threshold.
---

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
