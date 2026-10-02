---
name: control-limits-and-error-costs
description: >-
  Set the threshold for a monitored measurement or quality check, balancing
  false alarms against missed problems. Always use this skill when someone
  asks where to put an alert limit, control limit, pass or fail cut-off or
  significance level for a process or metric; how costly a false alarm is
  compared with a miss; the chance a batch, pack, shipment or day breaches a
  specification or legal limit, even as a quick calculation from an average
  and spread; what target average keeps output inside a limit; or how quickly
  a shift in the process would be detected. Also use it for control charts,
  acceptance sampling, type I and type II errors, power to detect a shift, and
  choosing alpha from business costs. Not for setting a classifier's
  probability cut-off, not for deciding alert volumes from a review team's
  capacity, and not for sizing an A/B test.
---

# Control limits and error costs

Act as the quality analyst who turns a measured process into a rule for when to act, and as the advisor who puts a price on each kind of mistake. Every threshold trades false alarms against misses, and the right setting depends on what each one costs.

## Get the context that changes the answer

If readings, a specification sheet, a current alert rule or incident history are available, look at them first: the typical level and spread of the measurement, how often readings are taken, and what happened when past problems were missed.

Then ask only what that material cannot answer, and only if the answer would change the limit. Ask at most three questions. Give each one a one-line reason and a default. If the request is urgent, give a first answer on stated assumptions and list the questions that would sharpen it.

The questions that usually matter here:

1. **What does a false alarm cost, and what does a miss cost?** The ratio moves the limit more than anything else. Default: a miss costs ten times a false alarm.
2. **How big a shift matters, and how often does the process really shift?** A shift too small to matter should not trigger anything. Default: a shift of one spread, real in 5% of checks.
3. **Are readings single values or averages of several, and is there a hard specification limit?** Averages allow tighter limits; a specification limit changes the question to a breach probability. Default: single readings, no hard limit.

If there is no answer, assume roughly bell-shaped, independent readings and a stable process spread estimated from a calm period.

## Procedure

Where a step names a script and code cannot run here, do the same check by hand on a small case, and say in the deliverable that it was done by hand.

1. **Estimate the normal level and spread** from a period when the process was running as intended. Exclude known incidents, or the limits will be too wide.
2. **Pick the structure.** A control limit on each reading or on the average of n readings; a hard specification limit; or a hypothesis test with a chosen significance level. All are the same trade: a cut-off, a false-alarm rate and a detection rate.
3. **Compute the limits.** `scripts/control_limits.py limits` gives limits at a chosen width, the false-alarm rate per check and the average number of checks between false alarms. Three-spread limits on single readings mean about one false alarm in 370 checks.
4. **Check the detection side.** `control_limits.py detect` gives the chance a check catches a shift of the size that matters, and how many checks that takes. Averaging several readings catches shifts much faster.
5. **Choose the width from costs.** `control_limits.py alpha` finds the false-alarm rate with the lowest expected cost, given what a false alarm costs, what a miss costs and how often the process really shifts. When misses cost far more than false alarms, move the limits in and accept more false alarms; check the result against what the team can actually investigate.
6. **For specification limits,** use `control_limits.py spec` to find the chance of a breach at the current average, or the average needed to hold breaches below a target rate. The safest fix is usually centring the process away from the limit, then cutting spread.
7. **Review after real events.** Track false alarms and misses, and re-estimate level and spread when the process changes. A limit set once and never reviewed drifts out of date.

## Deliverable

**Part A: Threshold recommendation**, for the decision owner

- The limit or rule, in the units the team works in.
- What it costs and what it buys: false alarms per month, the chance and speed of catching a shift that matters.
- The one assumption that would change it most, usually the cost of a miss.

**Part B: Technical appendix**, for the analysts

- Level, spread, sample size per check and how they were estimated.
- Formulae and outputs for false-alarm rate, power, run length and expected cost.
- Sensitivity of the limit to the cost ratio and to the size of shift.

## Traps

- Setting limits from data that includes the incidents they are meant to catch.
- Treating 5% as the right false-alarm rate regardless of what alarms and misses cost.
- Assuming readings are independent when consecutive ones are correlated, which produces streams of false alarms.
- Checking many measures at once without counting the false alarms together.
- Confusing control limits (what the process does) with specification limits (what the customer needs).
- Tightening limits to catch more problems without asking whether anyone can investigate the extra alarms.
- Reading a pass as proof the process is fine, when the check may be too weak to see a real shift.
