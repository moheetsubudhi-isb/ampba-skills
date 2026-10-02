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
