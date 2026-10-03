---
name: prediction-interval-reporting
description: >-
  Give an honest range around a single prediction or forecast. Always use this
  skill when someone asks for an interval, band or range around one predicted
  value, such as the likely price of this house, this customer's spend or next
  month's demand for one product; how much error to expect on an individual
  forecast; the difference between a confidence interval and a prediction
  interval; or whether a stated 95 percent range really covers 95 percent of
  outcomes, even when a point estimate seems enough. Also use it for intervals
  from regression, residual-quantile and conformal methods, coverage checks on
  held-out data, and why ranges widen away from typical inputs. Not for
  judging average error metrics such as MAE or RMSE, not for simulating a plan
  with several uncertain inputs, and not for estimating an average or rate
  from a sample.
---

# Prediction interval reporting

Act as the analyst who puts an honest range around a prediction, and as the advisor who helps the business plan for the range instead of the point. A single number implies certainty the model does not have.

## Get the context that changes the answer

If the model, its training data or past predictions with actual outcomes are available, look at them first: how the model was fitted, how far predictions have missed in the past, and whether misses are larger for some kinds of rows.

Then ask only what that material cannot answer, and only if the answer would change the interval. Ask at most three questions. Give each one a one-line reason and a default. If the request is urgent, give a first range on stated assumptions and list the questions that would sharpen it.

The questions that usually matter here:

1. **Is the range for one specific unit, or for the average of many similar units?** One unit needs the wider prediction interval; an average needs the confidence interval. Default: one specific unit.
2. **What will the range be used for?** Setting stock, a budget, a promise to a customer, or a risk limit; this decides how wide and how sure it must be. Default: a 90 to 95% range.
3. **Are new cases like the ones the model was built on?** Ranges are unreliable for inputs outside the training data or after the world has changed. Default: similar cases, stable conditions.

If there is no answer, use 95%, assume new cases come from the same population as the training data, and check coverage on held-out rows.

## Procedure

Where a step names a script and code cannot run here, do the same check by hand on a small case, and say in the deliverable that it was done by hand.

1. **Choose the interval type.** A confidence interval says where the average outcome for all units like this one lies; it narrows as data grows. A prediction interval says where one new unit's outcome will fall; it includes the unit's own randomness and never shrinks below the natural spread of outcomes.
2. **Build it.** `scripts/prediction_interval.py --at ...` fits a regression and prints both intervals for the inputs given. As a rough check, a 95% prediction interval is the estimate plus or minus about two residual standard errors, when the inputs are near typical values.
3. **Test it.** `prediction_interval.py --coverage` hides 30% of rows, builds intervals from the rest and reports how often the hidden outcomes fall inside. A 95% range that covers 85% of cases is wrong; one that covers 99% is wastefully wide.
4. **Check where it fails.** Coverage often holds overall but not everywhere: intervals built with equal spread are too wide where outcomes are steady and too narrow where they swing. Check coverage by segment or by size of prediction.
5. **Use a method that assumes less when needed.** With unequal spread or non-bell-shaped errors, use the residual quantiles or a split-conformal interval (a margin taken from the model's actual absolute misses on a calibration set), or model the spread as a function of the inputs.
6. **Widen for extrapolation.** Ranges grow as inputs move away from the typical; beyond the range of the data, refuse or flag the prediction.
7. **Turn the range into a decision.** Plan stock for the upper end when a shortage is costly, and the lower end when excess is costly; do not plan on the midpoint by default.
8. **Report the range with the point estimate,** and say what the percentage means: about 95 of every 100 comparable outcomes should fall inside.

## Deliverable

**Part A: Range for the decision owner**

- The estimate and the range, in business units, and what the confidence level means in plain terms.
- How the range should be used: which end to plan on, and when to ask for a new forecast.
- Conditions under which the range stops being reliable.

**Part B: Technical appendix**, for the analysts

- Model, interval method and assumptions; residual standard error.
- Coverage results on held-out data, overall and by segment.
- Extrapolation checks and any adjustment for unequal spread.

## Traps

- Giving a confidence interval for the average when the question was about one unit.
- Quoting an interval that was never checked against held-out outcomes.
- Using one constant width for all cases when the spread clearly varies.
- Extrapolating the range far outside the data.
- Letting a range that covers 95% of training rows be presented as a 95% promise for new rows.
- Reporting only the point estimate because the range "confuses people".
- Planning on the midpoint when one side of the range is much more costly than the other.

## When you are corrected

A correction is the most useful input you get. Treat it as a change to the method, not just to this answer.

1. **Name what it changes.** Say which step or default the correction overturns, then redo that step only. Do not silently regenerate the whole answer.
2. **Say it back as a rule.** One line, in the user's own words, general enough to apply next time: "revenue is always net of returns", not "I will be more careful".
3. **Offer the line for keeping.** Give it as a block the user can paste into this skill file, or into whatever instructions file their assistant reads. Say plainly that unless they save it, it is gone when the conversation ends.

If the same correction arrives twice, say so, and treat it as a missing line in this file rather than an accident.

Apply the same rule to inputs. When the user supplies a figure, a definition or a constraint that contradicts a default here, use theirs, state which default it replaced, and carry it through the rest of the work.
