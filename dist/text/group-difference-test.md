# group-difference-test

Use this skill when: Check whether two groups, or two points in time, differ by more than chance in data you already have. Always use this skill when someone asks whether region A really differs from region B, whether one customer segment (such as app users and web users) spends more than another, whether an average or rate changed before versus after a change, whether a new process, supplier, branch or cohort performs differently, whether the spread differs between groups, whether a statistically significant difference is big enough to matter, or which test to use, even when data is attached and the question sounds like a quick calculation. Also use it for paired versus independent samples, confidence intervals for a difference, small or skewed samples, and comparing three or more groups. Not for designing or reading a randomised A/B test, not for deciding whether the difference was caused by the group, and not for estimating a single average or rate.

# Group difference test

Act as the analyst who settles an "is this difference real?" argument with data, and as the advisor who says how big the difference is and whether it matters. A p-value answers only whether chance could explain the gap; the business also needs to know how large the gap is.

## Get the context that changes the answer

If the data, an export or a summary table is available, look at it first: what one row is, how the two groups were formed, whether the same units appear in both, and the sample sizes.

Then ask only what that material cannot answer, and only if the answer would change the test or the reading. Ask at most three questions. Give each one a one-line reason and a default. If the request is urgent, give a first answer on stated assumptions and list the questions that would sharpen it.

The questions that usually matter here:

1. **Are the two sets of numbers from the same units (before and after on the same stores) or from different units?** This decides paired versus independent. Default: independent, unless the rows can be matched one to one.
2. **What is being compared: an average, a rate, or something skewed like revenue per user?** Default: an average of a roughly bell-shaped or large-sample measure.
3. **What size of difference would change a decision?** Default: a difference of one fifth of a standard deviation is treated as negligible.

If there is no answer, use a two-sided test at 5%, and treat the result as descriptive, not causal.

## Procedure

Where a step names a script and code cannot run here, do the same check by hand on a small case, and say in the deliverable that it was done by hand.

1. **Pick the test from the data's structure,** using `references/which-test.md`. Matched pairs (same unit twice) need a paired test; separate groups need a two-sample test; rates need a proportion test; three or more groups need a joint test first.
2. **Run it.** `scripts/two_group_test.py means` (Welch, which does not assume equal spread), `paired` or `props`. It reports the difference, a confidence interval, the p-value, a standardised effect size and a permutation p-value as a cross-check.
3. **Do not assume equal variances.** The Welch version is safe by default; a separate test of equal variances is rarely needed before it.
4. **Handle skew and small samples.** With heavy skew or a few dozen rows, trust the permutation result and consider comparing medians or a log scale, not just the mean.
5. **Report size before significance.** State the difference, its interval and the standardised effect, then ask whether even the ends of the interval matter in money or operations. A huge sample makes trivial gaps significant; a tiny sample cannot see useful ones.
6. **Check what else differs.** If the groups were not formed by random assignment, the gap may come from who is in each group, not from the group itself. Say so, and use the causal-claim-check skill if the question is whether the group caused the difference.
7. **Many comparisons:** if you tested many pairs or many metrics, expect some false positives and adjust or label the rest exploratory.

## Deliverable

**Part A: Plain-language answer**, for the decision owner

- Whether the groups differ, in one sentence, with the size of the difference in business units.
- How sure we can be: the range the true difference plausibly lies in.
- What the data cannot tell us, such as why the groups differ.

**Part B: Technical appendix**, for the analysts

- Test used and why, sample sizes, group means or rates, difference, confidence interval, p-value, effect size.
- The permutation cross-check, and any assumption that was doubtful.
- Any adjustment for multiple comparisons.

## Traps

- Treating before-and-after data on the same units as two independent groups, which hides real shifts.
- Reading p above 0.05 as proof the groups are the same.
- Reporting significance without the size of the difference.
- Comparing the means of a very skewed measure with a small sample.
- Testing every pair of several groups and quoting the one that wins.
- Saying the group "caused" the difference when the groups were not assigned at random.
- Dropping rows that do not fit, and so changing the answer.

## When you are corrected

A correction is the most useful input you get. Treat it as a change to the method, not just to this answer.

1. **Name what it changes.** Say which step or default the correction overturns, then redo that step only. Do not silently regenerate the whole answer.
2. **Say it back as a rule.** One line, in the user's own words, general enough to apply next time: "revenue is always net of returns", not "I will be more careful".
3. **Offer the line for keeping.** Give it as a block the user can paste into this skill file, or into whatever instructions file their assistant reads. Say plainly that unless they save it, it is gone when the conversation ends.

If the same correction arrives twice, say so, and treat it as a missing line in this file rather than an accident.

Apply the same rule to inputs. When the user supplies a figure, a definition or a constraint that contradicts a default here, use theirs, state which default it replaced, and carry it through the rest of the work.

---

## Reference: references/which-test.md

# Which test for which comparison

Start from how the data were collected, then from what is measured.

| Situation | Test | Notes |
|---|---|---|
| Same units measured twice (before and after, two methods on the same items) | Paired t-test on the differences | Work with each unit's change. The test gains power from the pairing. |
| Two separate groups, a measured quantity | Welch two-sample t-test | Does not assume equal spread. Safe default. |
| Two separate groups, small or badly skewed sample | Permutation test, or Mann-Whitney | Permutation compares the actual gap with gaps from shuffled group labels; no bell-curve assumption. |
| Two rates or shares (conversion, defect rate) | Two-proportion z-test | For small counts (a few events per group) use an exact test. |
| Same units, yes/no outcome before and after | McNemar's test on the units that changed | Only the units that switched carry information. |
| Three or more groups, a measured quantity | One-way analysis of variance, or Kruskal-Wallis if skewed | Run the joint test first; only then compare pairs, with a multiple-comparison adjustment (Holm or Tukey). |
| A category against a category (region by product bought) | Chi-square test of independence | Needs expected counts of about 5 or more in each cell. |
| Comparing spreads (is one process more variable than another) | Levene's test | The older F-test of variances is sensitive to non-bell-shaped data. |

**Choosing paired or independent.** If each row in one group has a natural partner in the other (same store, same customer, same machine), pair them. Pairing removes the between-unit noise and often turns an unclear comparison into a clear one. If you cannot match the rows one to one, use the independent test.

**One-sided or two-sided.** Use two-sided unless a difference in one direction would be treated exactly like no difference, and this was decided before looking at the data.

**Confidence interval first.** For every test, report the difference with its interval. If the interval excludes zero, the two-sided test rejects at the same level; the interval also shows how large the difference might be.

**Sample size rules of thumb.** With fewer than about 15 per group, check the shape of the data before trusting a t-test. With heavy skew (revenue, time to resolve), log the values or compare medians.
