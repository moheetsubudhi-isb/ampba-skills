---
name: anomaly-detection
description: >-
  Find unusual transactions, sensor readings, log events, users or records,
  and choose the detection method: z-score or IQR rules, robust statistics,
  Mahalanobis distance, isolation forest, local outlier factor, or seasonal
  baselines for time series. Use whenever someone wants to detect fraud,
  suspicious payments, equipment faults, sudden spikes or drops, bot or attack
  traffic, or unusual behaviour with few or no labelled examples; set the
  contamination rate or anomaly score cut-off; turn a team's daily review
  capacity into an alert threshold; explain why a record was flagged; or test
  a detector against a handful of confirmed cases. Not for cleaning outliers
  from a training dataset before modelling, not for segmenting customers, and
  not for setting the threshold of a supervised classifier.
---

# Anomaly detection

Act as the analyst who finds what is unusual, and as the advisor who makes sure every alert is worth a person's time. An anomaly only matters if someone investigates it and acts.

## Get the context that changes the answer

If data, past alerts or confirmed cases are available, look at them first: volume per day, the features available, how normal behaviour varies by entity and time, and any labels.

Then ask only what that material cannot answer, and only if the answer would change the method or threshold. Ask at most three questions. Give each one a one-line reason and a default. If the request is urgent, give a first detector on stated assumptions and list the questions that would sharpen it.

The questions that usually matter here:

1. **What does a real problem look like, and are there any confirmed past cases?** Even a few dozen labelled cases let you measure precision instead of tuning blind.
2. **How many alerts can the team review per day, and what does a miss cost?** Review capacity sets the threshold, not a default contamination value.
3. **Is the unusual thing a single extreme value, an unusual combination of values, or a change over time?** This picks the method.

If there is no answer, assume no labels, capacity of about 50 reviews a day, anomalies that show up as unusual combinations, and an isolation forest checked against simple statistical rules.

## Procedure

Where a step names a script and code cannot run here, do the same check by hand on a small case, and say in the deliverable that it was done by hand.

1. **Define normal.** Choose the time window, the entity (per card, per machine, per merchant) and the seasonality. An anomaly measured against the wrong baseline is noise.
2. **Pick the method**, then load its reference.

   | Situation | Method | Load |
   |---|---|---|
   | One metric, roughly symmetric | z-score beyond ±3 | `references/statistical.md` |
   | One metric, skewed or already containing outliers | IQR rule or robust z-score (median and MAD) | `references/statistical.md` |
   | Several correlated numeric features | Mahalanobis distance | `references/statistical.md` |
   | A metric over time with trend and seasonality | Rules on residuals after removing the seasonal pattern | `references/statistical.md` |
   | Many features, mixed shapes, large data | Isolation forest | `references/isolation-forest-and-density.md` |
   | Groups of different density, anomalies in sparse pockets | Local outlier factor | `references/isolation-forest-and-density.md` |
   | Labels exist for most kinds of the problem | A supervised classifier instead | — |

3. **Build features that expose abnormal behaviour:** ratios to the entity's own history, counts in the last hour, distance from the usual location, time of day.
4. **Scale the features** and log-transform skewed amounts.
5. **Compare methods** with `scripts/anomaly_compare.py`. It scores records by univariate z-score, Mahalanobis distance and isolation forest, shows how far the methods agree, and lists the top records with the features that make each one unusual.
6. **Set the threshold from capacity:** flag the top N a day that the team can review. The contamination setting is only a starting point.
7. **Validate.** Measure precision among the top alerts on known cases or a reviewed sample. Record every reviewer's decision, so labels build up for a supervised model later.
8. **Explain each alert:** which features are far from normal, and by how much.
9. **Monitor** alert volume and reviewer hit rate. Refit on recent normal data when behaviour shifts.

## Deliverable

**Part A: Detection brief**, for the decision owner

- What gets flagged, how many alerts a day, and the estimated share that are real.
- What a reviewer sees for each alert.
- The cost of misses, and the plan to collect labels.

**Part B: Technical appendix**, for the builders

- Features, method, parameters and the score distribution.
- Validation results and the top examples with their reasons.
- The retraining and monitoring plan.

## Traps

- Single-metric rules that miss records unusual only in combination.
- Means and standard deviations inflated by the very outliers being hunted; use robust statistics.
- Leaving contamination at 10% and flooding the review team.
- One global model for entities whose normal levels differ widely.
- Deleting anomalies as bad data when they are the fraud.
- No feedback loop, so precision is never known.
