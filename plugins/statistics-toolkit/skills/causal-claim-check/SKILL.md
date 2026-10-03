---
name: causal-claim-check
description: >-
  Pressure-test a claim that one thing caused another before anyone acts on
  it. Always use this skill when someone asks whether X causes or drives Y,
  whether a correlation is causal or just confounding, whether a change,
  campaign, feature or policy really worked, what to control for when
  estimating an effect, whether an observational result can be trusted as a
  causal effect, whether an estimate was biased because the effect shrank or
  grew after adding a control, when an experiment is needed instead of
  regression with controls, or whether the groups being compared were alike to
  begin with, even when the question sounds like a simple yes or no. Also use
  it for selection bias, confounders and omitted variable bias. Not for
  designing or reading a randomised A/B test, not for reading the coefficients
  of a prediction model, and not for checking regression assumptions.
---

# Causal claim check

Act as the analyst who asks "compared with what?" and as the advisor who says how much weight a causal claim can bear. Most bad decisions come from a causal question answered with a comparison of groups that were already different.

## Get the context that changes the answer

If the analysis, the data dictionary or the original claim is available, look at it first: who received the treatment, how they came to receive it, what was measured before the treatment, and what the outcome is.

Then ask only what that material cannot answer, and only if the answer would change the verdict. Ask at most three questions. Give each one a one-line reason and a default. If the request is urgent, give a first verdict on stated assumptions and list the questions that would sharpen it.

The questions that usually matter here:

1. **Who decided who got the treatment?** Random assignment, a rule, the customers themselves or the business. Default: the units chose or were chosen, not randomised.
2. **What do you know about the units before the treatment?** Past outcomes and traits that drive both the treatment and the outcome. Default: only what is in the dataset.
3. **What decision hangs on this, and what would it cost to be wrong?** This sets how much evidence is enough. Default: a moderate-cost decision that can be reversed.

If there is no answer, treat the result as an association, not proof of cause, and say what is missing.

## Procedure

Where a step names a script and code cannot run here, do the same check by hand on a small case, and say in the deliverable that it was done by hand.

1. **Route the question.** If the aim is prediction (who will churn), causation is not needed and this skill is the wrong tool. If the aim is what would happen if we changed something, continue.
2. **Write the comparison.** For each unit there are two potential outcomes, with and without the treatment, and only one is observed. The observed difference between treated and untreated groups equals the true average effect plus selection bias: the difference that existed between the groups before any treatment.
3. **Check how the groups were formed.** Random assignment removes selection bias, so the simple difference is the effect. Anything else means the groups may differ systematically, such as customers who chose a plan, stores picked for a pilot, or regions where the team pushed hardest.
4. **Look for what drives both treatment and outcome.** Such variables (confounders) are what to control for. Run `scripts/omitted_variable_check.py` to see how the treatment coefficient moves when each control is added, how different the groups are on each control beforehand, and the exact identity: naive effect = adjusted effect + (control's effect on the outcome) × (how the control moves with the treatment). Use it to see the direction and size of the bias.
5. **Choose controls with care.** Add variables measured before the treatment that affect both treatment and outcome. Do not control for something the treatment itself changes (a step on the path to the outcome) or for something caused by both treatment and outcome; both distort the estimate. A strong correlation with the outcome alone is not a reason to add a variable.
6. **Accept the limit.** Controls fix only the differences you measured. If a driver of both treatment and outcome is unmeasured (motivation, intent to buy), the estimate remains biased, and the honest verdict is an upper or lower bound, not a number.
7. **Escalate the design when the stakes justify it.** Options are a randomised test, a natural experiment, matching on prior behaviour, difference-in-differences with a comparison group, or a cut-off rule; `references/design-alternatives.md` says when each works.
8. **Give a graded verdict:** shown, suggestive, or association only, with the reason.

## Deliverable

**Part A: Verdict for the decision owner**

- Can we say the change caused the result: yes, probably, or not shown, in one sentence.
- The size of the effect if we believe it, and how much of the raw difference came from who was in each group.
- The cheapest way to firm it up, such as a holdout or a test.

**Part B: Technical appendix**, for the analysts

- How treatment was assigned, the comparison made and the controls used, with the reason for each.
- Coefficient on the treatment with and without controls, the balance table and the identity check.
- Unmeasured drivers considered, and any alternative design proposed.

## Traps

- Comparing customers who opted in with customers who did not and calling the gap the effect.
- Controlling for a variable the treatment changes, and so erasing part of the effect.
- Controlling for a variable caused by both treatment and outcome, which creates a false link.
- Adding every available variable and treating the result as cause and effect.
- Reading a small shift in the coefficient after adding controls as proof that nothing else matters.
- Claiming a cause from a before-and-after change with no comparison group.
- Saying "we controlled for it" about something measured poorly.

## When you are corrected

A correction is the most useful input you get. Treat it as a change to the method, not just to this answer.

1. **Name what it changes.** Say which step or default the correction overturns, then redo that step only. Do not silently regenerate the whole answer.
2. **Say it back as a rule.** One line, in the user's own words, general enough to apply next time: "revenue is always net of returns", not "I will be more careful".
3. **Offer the line for keeping.** Give it as a block the user can paste into this skill file, or into whatever instructions file their assistant reads. Say plainly that unless they save it, it is gone when the conversation ends.

If the same correction arrives twice, say so, and treat it as a missing line in this file rather than an accident.

Apply the same rule to inputs. When the user supplies a figure, a definition or a constraint that contradicts a default here, use theirs, state which default it replaced, and carry it through the rest of the work.
