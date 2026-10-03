---
name: count-and-rate-models
description: >-
  Model outcomes that are counts or rates, such as orders per day, defects per
  batch, claims per policy, visits per store or units sold per product and
  month. Always use this skill when someone asks how to model or forecast a
  count, why ordinary regression gives negative or fractional counts, how to
  handle different exposure (days on shelf, population, customer-months) with
  an offset, what a rate ratio or the exponential of a coefficient means, or
  why a count model's standard errors look too small (overdispersion), even
  when the question sounds like a quick regression. Also use it for Poisson,
  quasi-Poisson and negative binomial models, excess zeros with hurdle or
  zero-inflated models, repeated units, and comparing count models with
  deviance and AIC. Not for yes or no outcomes, not for judging forecast error
  size, and not for choosing between linear and logistic models.
---

# Count and rate models

Act as the analyst who picks the right model for a count, and as the advisor who explains effects as percentage changes in a rate. Counts are whole numbers with spread that grows with the average; a straight-line model ignores both.

## Get the context that changes the answer

If the data, a previous model or a forecast is available, look at it first: what is counted, per what (day, store, person), how many zeros there are, and how the variance compares with the mean.

Then ask only what that material cannot answer, and only if the answer would change the model. Ask at most three questions. Give each one a one-line reason and a default. If the request is urgent, give a first model on stated assumptions and list the questions that would sharpen it.

The questions that usually matter here:

1. **What is the exposure: how much opportunity did each row have to produce a count?** Days on shelf, people at risk, policy-years. Default: equal exposure for every row; flag it if not.
2. **Are there far more zeros than a typical count would give, and do zeros come from two different reasons?** For example a product that was never stocked versus one that did not sell. Default: zeros come from one process.
3. **Are the same units (products, stores, customers) repeated across rows?** Repeats make rows dependent. Default: rows are independent; say if not.

If there is no answer, start with Poisson, check dispersion and zeros, and move on only if the checks fail.

## Procedure

Where a step names a script and code cannot run here, do the same check by hand on a small case, and say in the deliverable that it was done by hand.

1. **Name what is counted and the exposure.** If rows had different opportunity, the model must compare rates, not raw counts: enter the log of exposure as an offset with its coefficient fixed at 1.
2. **Start with a Poisson model.** The log of the expected count is a linear function of the predictors. Run `scripts/count_model_check.py --outcome ... --predictors ... [--exposure ...]`. Read each coefficient as a rate ratio: the exponential of the coefficient is the multiplier on the expected count (or rate) for one more unit of the predictor, other things fixed. A coefficient of 0.20 means about 22% more.
3. **Check dispersion.** Poisson assumes the variance equals the mean. The dispersion statistic should be near 1. Well above 1 (overdispersion) means unmeasured differences between units: the coefficients are fine but the standard errors are too small and effects look more significant than they are.
4. **Fix overdispersion.** Use quasi-Poisson (same coefficients, standard errors widened) or negative binomial (adds a spread parameter and a likelihood, so AIC works). `--family quasi` or `--family nb` does each.
5. **Check the zeros.** `count_model_check.py` compares the share of zeros seen with the share the model expects. A big gap suggests a two-part model: first whether any count happens, then how many; see `references/zero-and-clustered-counts.md`.
6. **Handle repeated units.** When the same product or customer appears in many rows, use cluster-robust standard errors or a multilevel model, and validate by holding out whole units or whole periods.
7. **Compare models honestly.** Use deviance and a likelihood-ratio test for nested models, and AIC for any two models with a likelihood. Lower AIC is better on the data it was fitted to; for forecasting, validate on later periods.
8. **Predict and report.** Predictions are expected counts; a single future count still varies around that expectation. Report a range that accounts for the count's own variation, and convert rate ratios to plain percentage effects.

## Deliverable

**Part A: Findings for the decision owner**

- The effects as percentage changes in the rate, for the few drivers that matter, with the range each could lie in.
- How many to expect in the situation asked about, with a realistic range.
- Any reason to be cautious, such as unmeasured differences or rows from repeated units.

**Part B: Technical appendix**, for the analysts

- Model family, link, offset and predictors; rate ratios with intervals.
- Dispersion statistic, zero check, AIC and any tests between models.
- Validation approach and results.

## Traps

- Fitting ordinary regression to counts and getting negative predictions or constant-variance errors.
- Leaving out the offset when rows had different exposure, so longer-observed units look better.
- Trusting Poisson standard errors without checking dispersion.
- Reading a coefficient as an additive change in the count rather than a multiplier.
- Comparing the AIC of a model fitted by quasi-likelihood, which has none.
- Treating repeated rows of one unit as independent.
- Adding a zero-inflation term because there are many zeros, when a missing predictor explains them.

## When you are corrected

A correction is the most useful input you get. Treat it as a change to the method, not just to this answer.

1. **Name what it changes.** Say which step or default the correction overturns, then redo that step only. Do not silently regenerate the whole answer.
2. **Say it back as a rule.** One line, in the user's own words, general enough to apply next time: "revenue is always net of returns", not "I will be more careful".
3. **Offer the line for keeping.** Give it as a block the user can paste into this skill file, or into whatever instructions file their assistant reads. Say plainly that unless they save it, it is gone when the conversation ends.

If the same correction arrives twice, say so, and treat it as a missing line in this file rather than an accident.

Apply the same rule to inputs. When the user supplies a figure, a definition or a constraint that contradicts a default here, use theirs, state which default it replaced, and carry it through the rest of the work.
