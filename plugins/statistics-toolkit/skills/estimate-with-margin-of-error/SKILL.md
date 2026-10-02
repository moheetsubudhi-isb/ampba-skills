---
name: estimate-with-margin-of-error
description: >-
  Estimate a true average or rate from a sample and say how precise it is, or
  work out how big a sample is needed. Always use this skill when someone asks
  for a confidence interval or margin of error, what a survey, audit,
  inspection or quality sample says about the whole population, how many
  records, customers or units to sample for a target precision, whether a
  sample is big enough to trust, whether to use a t or z interval for a small
  sample, or how to explain a confidence interval to a manager, even when the
  question sounds like a quick check. Also use it for intervals for
  proportions with small counts or rates near zero or one, finite populations,
  and sampling pitfalls such as convenience samples and non-response. Not for
  comparing two groups, not for sizing an A/B test, and not for explaining
  what a confidence interval means when no data is in play.
---

# Estimate with a margin of error

Act as the analyst who turns a sample into a number the business can plan on, and as the advisor who says how far that number could be off. A single figure from a sample is a guess until it carries a margin of error.

## Get the context that changes the answer

If the sample, an audit file or survey results are available, look at them first: how the sample was drawn, how many rows, how many responded, and the spread of the values.

Then ask only what that material cannot answer, and only if the answer would change the estimate or the sample size. Ask at most three questions. Give each one a one-line reason and a default. If the request is urgent, give a first answer on stated assumptions and list the questions that would sharpen it.

The questions that usually matter here:

1. **How was the sample chosen?** Random, or whoever was easy to reach or chose to answer. A biased sample gives a precise wrong answer. Default: treat it as random, and say it is an assumption.
2. **How precise does the answer need to be, and how sure?** The margin the decision can tolerate, at 95% unless the stakes call for more. Default: 95% confidence.
3. **How big is the whole population, and what is the spread or the expected rate?** A small population needs fewer records; an unknown rate is planned at 50%, the worst case. Default: a large population and a 50% rate.

If there is no answer, use 95% confidence, a large population and the worst-case spread for a rate.

## Procedure

Where a step names a script and code cannot run here, do the same check by hand on a small case, and say in the deliverable that it was done by hand.

1. **Check the sample before the arithmetic.** Was every unit equally likely to be chosen? Who is missing (non-responders, records with missing fields, units that are hard to reach)? No formula repairs a sample that left out a whole kind of unit.
2. **Estimate the average.** The interval is the sample average plus or minus a multiplier times the standard error (spread divided by the square root of n). Use the t multiplier, which is wider for small samples; `scripts/margin_of_error.py mean` does this.
3. **Estimate a rate.** Use the Wilson interval for proportions; `margin_of_error.py prop` shows it beside the textbook interval. The textbook interval breaks down for small counts and for rates near 0% or 100%: with zero events in 40, the honest upper bound is about 9%, not 0%.
4. **Plan a sample size.** `margin_of_error.py size` gives the n for a target half-width. Halving the margin needs four times the sample. For a rate with no prior guess use 50%; for a small population apply the finite-population correction.
5. **Say what the interval means.** Across many repeats of the same sampling method, about 95% of such intervals would contain the true value. It is not a 95% chance that this particular sample mean is right, and it does not cover bias or bad measurement.
6. **Match the precision to the decision.** If the whole interval leads to the same action, stop sampling. If the action flips inside the interval, more data is worth paying for up to the point the interval is narrow enough.
7. **Report what is uncertain beyond sampling:** non-response, measurement error and a population that changed since the sample.

## Deliverable

**Part A: Estimate and range**, for the decision owner

- The estimate and its margin in plain terms, for example "about 6% of invoices are wrong, somewhere between 3% and 12%".
- Whether the sample is enough for the decision, or how many more are needed.
- The main reason the real error could be larger than the stated margin.

**Part B: Technical appendix**, for the analysts

- Sampling method, n, estimate, standard error and method used for the interval.
- Sample-size calculation with its assumptions.
- Checks on missing or excluded units.

## Traps

- Quoting the margin of error of a self-selected sample as if it were random.
- Using the bell-curve interval for a rate with a handful of events.
- Forgetting that a margin of error covers sampling luck only, not bias.
- Planning a sample size from a spread guessed too low.
- Applying the finite-population correction to a sample that is not random.
- Reading the interval as the range of individual values.
- Stopping at a sample size chosen for a different precision than the decision needs.
