---
name: model-selection-and-validation
description: >-
  Choose a model family, design validation that proves the model will
  generalise, and diagnose overfitting or underfitting. Use when someone asks
  which algorithm to use; how to split training and test data; about
  cross-validation, or stratified, grouped or time-based splits;
  hyperparameter tuning or grid search; regularisation, tree depth or
  pruning; k for k-nearest neighbours; bias and variance; learning curves;
  why test performance is much worse than training; whether more data would
  help; or why a model that validated well failed after launch. Not for
  choosing a decision threshold or business metric for a classifier, and not
  for cleaning or auditing the dataset.
---

# Model selection and validation

Act as the data scientist who picks and proves the model, and as the advisor who explains the trade-off. The goal is the simplest model that reliably beats the current way of working, validated the way it will actually be used.

## Get the context that changes the answer

If data is available, look at it first. Check row count, time columns, repeated entities and target type.

Then ask only what the data and the request cannot answer, and only if the answer would change the split or the model. Ask at most three questions. Give each one a one-line reason and a default. If the request is urgent, run a first comparison on stated assumptions.

The questions that usually matter here:

1. **Will the model predict forward in time, or for new customers, stores or devices not seen in training?** This decides between random, temporal and grouped splits. A random split on such data leaks silently and inflates every score.
2. **What matters besides accuracy?** Explainability for a regulator or manager, prediction latency, retraining cost, the size of the data.
3. **What is the baseline today?** A rule, a current model, a human decision, or a simple average. The new model has to beat it by a margin that matters.

## Procedure

1. **Establish baselines first.** A dummy model (majority class or mean), plus today's rule or process.
2. **Design the split.** Load `references/cv-design.md`. Use the test set exactly once, at the end.
3. **Shortlist models** from data size, structure and constraints. Load `references/model-choice.md`.
4. **Put every preprocessing step inside the pipeline:** imputers, encoders, scalers, feature selection. Cross-validate the whole pipeline. Anything fitted before the split leaks.
5. **Sweep complexity and read bias versus variance.** Plot training and validation scores across the complexity knob: tree depth, k in KNN, regularisation strength, or boosting rounds with learning rate. Run `scripts/bias_variance_check.py` for a quick read.
   - **Both scores low:** underfitting. Add features, or allow more complexity.
   - **Training high, validation much lower:** overfitting. Regularise, simplify, prune, or add data.
   - **Scores vary widely across folds:** the estimate itself is unstable. Report the spread.
6. **Tune honestly.**
   - Use grid search for up to about three hyperparameters, and random or Bayesian search beyond that.
   - Keep a final hold-out set, or use nested cross-validation for the reported score.
   - Never tune on the test set.
7. **Check the learning curve.** If validation scores still rise as training data grows, more data will help. If they have flattened, spend effort on features instead.
8. **Choose as an advisor.** Prefer the simplest model whose validation score sits within one standard error of the best. Weigh explainability, latency and maintenance against small gains.

## Deliverable

**Part A: Model brief**

- The recommended model, and its expected performance as a mean with a range, against the baseline.
- Why it beats the runner-up, and what would change that choice.
- A retraining and monitoring plan.

**Part B: Technical appendix**

- The split design.
- A candidates table: model · cross-validated mean · standard deviation · train score · fit time.
- The tuning grid, and the learning and complexity curves.
- Seeds, so results can be reproduced.

## Traps

- A random split on time-ordered data.
- The same customer in both training and test data.
- Scaling or encoding on the full data before splitting.
- Tuning against the test set, or reporting the best single fold.
- Picking a complex model for a gain smaller than the spread across folds.
- Accuracy on imbalanced classes. Hand metric choice to a proper threshold analysis.
