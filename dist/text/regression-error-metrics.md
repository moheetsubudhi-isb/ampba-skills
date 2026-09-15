# regression-error-metrics

Use this skill when: Judge whether a regression or forecast model's errors are good enough, and choose the error metric the business should see: MAE, RMSE, MAPE, WAPE, R-squared, bias, or a cost-weighted error. Use whenever someone asks whether an RMSE, MAE or MAPE value is good; why R-squared is high but predictions are still useless, or negative on test data; which metric to report for price, demand, delivery-time, sales or salary predictions; why MAPE explodes when actual values are small; how to compare a model with a naive, last-period or average baseline; how errors differ across segments or ranges; whether over- and under-prediction cost the same; or how to read a residual plot for a predictive model. Not for classification metrics or thresholds, not for ranking or recommender metrics, and not for testing whether a coefficient is statistically significant.

# Regression error metrics

Act as the data scientist who measures prediction error, and as the advisor who turns it into money or time the business understands. An error number means nothing until it is compared with a baseline and with the cost of acting on a wrong prediction.

## Get the context that changes the answer

If predictions, actuals or model output are available, look at them first: the range of actual values, zeros and small values, segments, and time order.

Then ask only what that material cannot answer, and only if the answer would change the metric or the verdict. Ask at most three questions. Give each one a one-line reason and a default. If the request is urgent, give a first assessment on stated assumptions and list the questions that would sharpen it.

The questions that usually matter here:

1. **What decision uses the prediction, and what does an error cost?** Over-forecasting demand wastes stock; under-forecasting loses sales. Unequal costs need a different metric.
2. **What does the business use today?** Last period's value, a rule, or a planner's estimate. That is the baseline the model must beat.
3. **Are there zeros or very small actual values, and do some segments matter more?** Small values break percentage errors; high-value items may deserve more weight.

If there is no answer, assume errors cost the same in both directions, a last-period or average baseline, and report MAE, WAPE and RMSE together.

## Procedure

Where a step names a script and code cannot run here, do the same check by hand on a small case, and say in the deliverable that it was done by hand.

1. **Evaluate on data the model never saw**, split the way it will be used: by time for anything forecast.
2. **Compute the metrics against baselines** with `scripts/regression_error_check.py`: MAE, RMSE, MAPE (with the count of rows excluded for zero actuals), WAPE, R-squared and bias, for the model and a baseline, overall and by segment.
3. **Choose the headline metric.**

   | Situation | Metric |
   |---|---|
   | Error cost grows in proportion to its size; explain in the target's units | MAE |
   | Large errors are disproportionately costly | RMSE |
   | Compare items or series of different scales, with no zeros or tiny values | MAPE |
   | Aggregate across items where some actuals are small or zero | WAPE: total absolute error ÷ total actual |
   | Over- and under-prediction cost differently | Cost-weighted error, or quantile loss at the matching quantile |
   | Share of variation explained, relative to predicting the mean | R-squared, never on its own |

4. **Read R-squared carefully.** It compares the model with predicting the mean. It can be high while errors are still too large to act on, negative on test data when the model does worse than the mean, and it cannot be compared across datasets with different spreads.
5. **Break the errors down** by segment, by size of the actual value, and over time. Look for bias (average error away from zero), errors that grow with the value, and segments that fail.
6. **Read the residual plot** of errors against predictions. A curve means a missing non-linear effect; a funnel suggests modelling the log of the target or relative error.
7. **Translate into business terms:** "on average we miss delivery time by 1.8 days, and 90% of orders land within ±4 days", and the cost of errors at current volume against the baseline's.
8. **Report a range, not only a point:** error percentiles or prediction intervals.

## Deliverable

**Part A: Accuracy brief**, for the decision owner

- How far off predictions typically are, in business units.
- The improvement over what the business uses today.
- Where the model fails, and whether it is good enough for the decision.

**Part B: Technical appendix**, for the builders

- A metric table for the model and baselines, on test data.
- The segment and range breakdown, and bias.
- Residual findings and metric definitions.

## Traps

- Reporting R-squared alone.
- MAPE with actual values at or near zero.
- Metrics computed on training data.
- Comparing RMSE across targets with different units or scales.
- Averaging MAPE across items so tiny items dominate.
- A random split for a time series.
- Reporting errors in standardised units after scaling the target.
- A good average hiding a systematic bias in one segment.
