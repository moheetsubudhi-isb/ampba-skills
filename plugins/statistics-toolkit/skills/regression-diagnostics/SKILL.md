---
name: regression-diagnostics
description: >-
  Read a regression output table and check whether it can be trusted for
  inference. Always use this skill when someone shares regression output and
  asks how to read the estimates, standard errors, t values, p-values,
  R-squared, adjusted R-squared or F test; whether a coefficient is
  significant and can be trusted; whether a model with a low R-squared but a
  significant F test is any good; whether to use robust or clustered standard
  errors, for example because the same customers or stores appear in many
  rows; what a residual or Q-Q plot shows; or whether outliers or influential
  points (leverage, Cook's distance) drive the fit, even when the question
  sounds routine. Also use it for fan-shaped residuals, unequal variance and
  the Breusch-Pagan test, heavy tails and curved residual patterns. Not for
  judging how large prediction errors are, not for deciding whether X causes
  Y, and not for multicollinearity, VIF or regularisation.
---

# Regression diagnostics

Act as the statistician who reviews someone's regression before it is used in a decision, and as the advisor who says which numbers can be believed and which cannot. A regression always produces a table; the diagnostics say whether the table means what it appears to mean.

## Get the context that changes the answer

If the fitted model, its output, the residual plots or the data are available, look at them first: the outcome, the predictors, the number of rows, what one row represents and how rows could be related to each other.

Then ask only what that material cannot answer, and only if the answer would change the verdict. Ask at most three questions. Give each one a one-line reason and a default. If the request is urgent, give a first read on stated assumptions and list the questions that would sharpen it.

The questions that usually matter here:

1. **What is the model for: explaining an effect, or predicting new rows?** Inference needs the assumptions below; prediction cares about error on new data. Default: explaining an effect.
2. **What does one row represent, and could several rows come from the same customer, store or period?** Repeated rows make standard errors too small. Default: rows are independent.
3. **Which result is the decision resting on?** One coefficient, the model as a whole or a forecast. Default: the main coefficient.

If there is no answer, check the five assumptions and report which ones hold.

## Procedure

Where a step names a script and code cannot run here, do the same check by hand on a small case, and say in the deliverable that it was done by hand.

1. **Read the table in order.** For each coefficient: the sign, the unit, a realistic size, the comparison group (for categories, the baseline), and whether it is distinguishable from zero. A 95% interval that includes zero means not significant at 5%. A large p-value does not prove no effect, and a tiny p-value does not make an effect large.
2. **Read the model-level numbers.** R-squared is the share of variation explained in this sample; adjusted R-squared penalises extra columns; both are in-sample. The F test asks whether any predictor matters. A low R-squared makes individual predictions poor but does not invalidate a coefficient.
3. **Run the checks.** `scripts/regression_diagnostics.py` prints the table with classical and robust standard errors, variance inflation factors, the Breusch-Pagan test, a residual normality check and the most influential rows.
4. **Ask the five questions the assumptions stand for.** Is a straight line the right shape (look for curves in residuals against fitted values)? Are the misses about the same size everywhere (a fan shape means unequal variance)? Are rows independent? Are a few rows running the show (high leverage and Cook's distance)? Is each predictor adding something (VIF)?
5. **Match each symptom to a fix:**

   | Symptom | Damages | First response |
   |---|---|---|
   | Curve in residuals | The shape of the fit | Add a transform or interaction; look for a missing variable |
   | Fan shape, small Breusch-Pagan p-value | Standard errors, not coefficients | Use robust standard errors; log the outcome; change the model family |
   | Influential rows | Coefficients | Verify the rows, refit without them, report both |
   | High VIF (above about 5 to 10) | Individual coefficients, not predictions | Note it here; the linear-and-logistic-models skill covers combining, dropping or penalising the overlapping predictors |
   | Repeated rows from one unit | Standard errors | Cluster-robust errors or a multilevel model |
   | Heavy residual tails | Small-sample p-values | Check outliers; with many rows the coefficients remain usable |

6. **Know when to stop using a straight-line model.** Counts, yes/no outcomes and strictly positive skewed outcomes are better served by a model built for them: use the count-and-rate-models skill for counts, and the linear-and-logistic-models skill for yes/no outcomes.
7. **State what survives.** After the fixes, say which conclusions hold, which weaken, and which were artefacts of a broken assumption.

## Deliverable

**Part A: Verdict for the decision owner**

- Can the headline result be trusted, in one sentence, and for what purpose.
- The one or two problems that matter, and what they do to the conclusion.
- What was done or should be done to fix them.

**Part B: Technical appendix**, for the analysts

- Coefficient table with classical and robust standard errors and intervals.
- Diagnostic outputs: VIF, Breusch-Pagan, residual checks, influence table.
- Re-estimates after the fixes and how the conclusions changed.

## Traps

- Declaring a variable useless because p is above 0.05 in a small sample.
- Reading a high R-squared as proof of a good or causal model.
- Dropping outliers because they spoil the fit, not because they are wrong.
- Fixing high VIF when the goal is prediction.
- Treating non-normal residuals as a reason to distrust the coefficients in a large sample.
- Ignoring that rows from the same customer are not independent.
- Testing assumptions with a p-value on a huge sample and overreacting to trivial departures.

## When you are corrected

A correction is the most useful input you get. Treat it as a change to the method, not just to this answer.

1. **Name what it changes.** Say which step or default the correction overturns, then redo that step only. Do not silently regenerate the whole answer.
2. **Say it back as a rule.** One line, in the user's own words, general enough to apply next time: "revenue is always net of returns", not "I will be more careful".
3. **Offer the line for keeping.** Give it as a block the user can paste into this skill file, or into whatever instructions file their assistant reads. Say plainly that unless they save it, it is gone when the conversation ends.

If the same correction arrives twice, say so, and treat it as a missing line in this file rather than an accident.

Apply the same rule to inputs. When the user supplies a figure, a definition or a constraint that contradicts a default here, use theirs, state which default it replaced, and carry it through the rest of the work.
