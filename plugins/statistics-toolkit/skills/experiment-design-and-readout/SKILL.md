---
name: experiment-design-and-readout
description: >-
  Design and read randomised experiments and A/B tests. Always use this skill
  when someone asks how many users or how long a test needs to run, the
  smallest effect a given sample can detect, whether a lift or difference
  between variants is real or just noise (even when given only the counts for
  each variant), whether to ship the winning variant, whether an uneven split
  such as 52 percent to 48 percent matters, or why a result keeps changing
  while the test runs, even when the question sounds like a quick yes or no.
  Also use it for choosing the randomisation unit, power, guardrail metrics,
  peeking and stopping early, several variants or metrics at once, and
  novelty effects. Not for comparing groups that were not randomised, not for
  deciding whether X caused Y in observational data, not for offline
  evaluation of a recommender, and not for explaining what an A/B test is when
  no test is in play.
---

# Experiment design and readout

Act as the experimentation lead who designs the test before it starts, and as the advisor who tells the business whether the result is safe to act on. A test is only worth running if someone has agreed beforehand what result would change the decision.

## Get the context that changes the answer

If a test plan, a dashboard export or raw counts are available, look at them first: who was assigned, how, for how long, how many users in each arm, and which metric was the goal.

Then ask only what that material cannot answer, and only if the answer would change the design or the call. Ask at most three questions. Give each one a one-line reason and a default. If the request is urgent, give a first answer on stated assumptions and list the questions that would sharpen it.

The questions that usually matter here:

1. **What is the one metric that decides, and what is its current level?** Sample size depends on the baseline rate or spread. Default: a conversion-style rate, with the current rate taken from the last four weeks.
2. **What is the smallest change worth acting on?** A test that can only detect huge effects is a waste. Default: the change that would pay for building and running the variant.
3. **What is the unit of assignment, and how much traffic is there?** Users, sessions, stores or accounts; this sets the real sample and the duration. Default: one user, one arm for the whole test.

If there is no answer, assume 95% confidence, 80% power, a two-sided test, and a full-week minimum run.

## Procedure

Where a step names a script and code cannot run here, do the same check by hand on a small case, and say in the deliverable that it was done by hand.

1. **Write the decision first.** Primary metric, the smallest effect that matters, what you will do for a win, a loss and a flat result, and a few guardrail metrics that must not get worse (speed, errors, refunds).
2. **Randomise at the right level.** Assign by the unit whose behaviour one arm could change for another: a user for a page test, a store for a pricing test. Randomise once, keep users in their arm, and never let people choose their arm.
3. **Size the test.** Run `scripts/ab_test_plan.py plan --baseline ... --lift ...` for a rate, or `--sd ... --effect ...` for an average. Halving the detectable effect roughly quadruples the sample. Convert to days at real traffic and round up to whole weeks so every weekday is covered equally. If the run is too long to be practical, raise the minimum effect, use a more sensitive metric, or accept that the test cannot answer this question.
4. **Fix the stopping rule in advance.** Decide the end date or sample and do not stop early on a good-looking result: checking repeatedly and stopping at the first significant reading produces false wins far more often than 5% of the time (the script's selftest shows the size of the effect). If early stopping matters, use a sequential design agreed beforehand.
5. **Check the assignment before the result.** Compare the observed split with the intended split: `ab_test_plan.py read` flags a sample ratio mismatch. A mismatch means assignment or logging is broken, and the result cannot be trusted whatever the p-value says.
6. **Read the result.** Report the difference with its confidence interval and relative lift, not only the p-value. Ask whether even the low end of the interval is worth shipping, and whether the guardrails held.
7. **Handle many looks.** With several variants or many metrics, some will look significant by chance: name one primary metric, treat the rest as exploratory, and apply a correction if a decision rests on one of several.
8. **Watch for novelty and ramp-up.** An early lift that fades is often curiosity. Look at the effect by week before trusting a short test, and plan a holdout for big launches.
9. **When randomising is not possible,** say so and hand over to the causal-claim-check skill instead of calling a before-and-after comparison an experiment.

## Deliverable

**Part A: Test brief or decision**, for the decision owner

- Before the test: what will be tested, for how long, how many users, and what result leads to what action.
- After the test: ship, do not ship, or extend, in one sentence, with the size of the effect and the range it could plausibly be.
- Anything that weakens the result (mismatched split, novelty effect, short run).

**Part B: Technical appendix**, for the analysts

- Assumptions: baseline, minimum effect, alpha, power, sample size per arm, unit of assignment.
- Observed counts, the difference, confidence interval, p-value and the split check.
- Guardrail results, segments examined and any corrections applied.

## Traps

- Stopping as soon as the result turns significant.
- Sizing the test on a hoped-for effect larger than anything plausible.
- Reading "not significant" as "no effect": a small test cannot rule out a useful effect.
- Reporting a p-value with no effect size or interval.
- Slicing the result into many segments until one is significant.
- Changing the variant, the metric or the traffic split mid-test.
- Assigning by user but analysing by session, which overstates the sample.
- Ignoring a sample ratio mismatch because the lift looks good.
