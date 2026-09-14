# classification-metrics-and-threshold

Use this skill when: Judge a classifier by what its errors cost, and set the decision threshold. Use when someone reports accuracy, precision, recall, F1, ROC-AUC or PR-AUC and asks what counts as good; when a model looks accurate but misses the cases that matter; when classes are imbalanced, as in fraud, churn, loan default, defects or medical screening; when choosing a probability cutoff; when comparing two classifiers; when reading a confusion matrix; when a review team can handle only so many alerts a day; or when checking whether predicted probabilities are calibrated. Not for choosing the algorithm or designing cross-validation, and not for ranking metrics for recommender systems.

# Classification metrics and threshold

Act as the data scientist who evaluates the model, and as the advisor who turns its scores into an operating decision. A classifier is not good or bad in the abstract. It is good or bad at a particular threshold, for particular costs.

## Get the context that changes the answer

If labels and scores are available, look at them first. Check the base rate, the score distribution, and the confusion matrix at 0.5.

Then ask only what the data cannot reveal, and only if the answer would change the recommendation. Ask at most three questions. Give each one a one-line reason and a default. If the request is urgent, show the trade-off at several thresholds now, and pin the threshold once costs are known.

The questions that usually matter here:

1. **What does a false positive cost compared with a false negative?** Money, staff time, customer harm. Without this, no threshold recommendation is possible — only a list of metrics. A rough ratio is enough to start, such as "a missed fraud costs about 50 times a wasted review."
2. **How many flagged cases can be acted on per day or week?** Review capacity often sets the threshold more than cost does.
3. **Will the base rate in production differ from the training data?** Precision moves with the base rate.

## Procedure

Where a step names a script and code cannot run here, do the same check by hand on a small case, and say in the deliverable that it was done by hand.

1. **Anchor on the base rate.** At 2% fraud, a model that flags nothing is 98% accurate. Report the base rate and the dummy baseline next to every metric.
2. **Show the confusion matrix in business units:** cases, rupees, hours.
3. **Match the metric to the purpose.**
   - **Precision:** when every alert costs effort, or annoys a customer.
   - **Recall:** when a miss is expensive or harmful.
   - **F-beta:** when one matters more. F2 weights recall double.
   - **PR-AUC over ROC-AUC for rare positives.** ROC-AUC looks flattering when negatives vastly outnumber positives.
   - **Log-loss or Brier score:** when the probabilities themselves are used downstream, for pricing or expected value.
4. **Set the threshold from the business.** Run `scripts/threshold_by_cost.py`. It reports the threshold that minimises expected cost, the threshold that fits review capacity, and the threshold that meets a required recall — each with its precision, recall and cost.
5. **Check calibration** when probabilities drive decisions. Draw a reliability curve on held-out data. Recalibrate if it is off, using isotonic or Platt scaling fitted on a separate split.
6. **Adjust for base-rate shift.** If the production base rate differs, recompute precision and expected cost at that rate.
7. **Compare models at the operating point,** not by AUC alone. The model with the higher AUC can lose at the threshold you will actually use.
8. **Check key segments** when decisions affect people. Compare error rates across regions, customer types, or protected groups where lawful to measure.

## Deliverable

**Part A: Decision brief**

- The recommended threshold, stated operationally. Example: "Flag about 340 claims a day. This catches about 81% of fraud, and about 1 flag in 4 is real."
- Expected cost or benefit against the current process.
- A trade-off table at three thresholds: conservative, recommended, aggressive.

**Part B: Technical appendix**

- Confusion matrices, PR and ROC curves, and the calibration curve.
- The cost assumptions used, and how sensitive the threshold is to them.

## Traps

- Reporting accuracy on imbalanced data.
- Using 0.5 as the threshold because it is the default.
- Choosing between models by ROC-AUC when positives are rare.
- Treating uncalibrated scores as probabilities.
- Setting the threshold on the test set, then reporting performance on the same set.
- Ignoring review capacity, which leaves thousands of alerts nobody can work through.
