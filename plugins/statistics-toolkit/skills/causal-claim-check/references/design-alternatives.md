# Designs for cause and effect, and when each one works

Use the simplest design that removes the selection bias you actually face.

| Design | Idea | Works when | Main risk |
|---|---|---|---|
| Randomised test | Assign treatment by chance | You control who gets what, and it is ethical and affordable | Spillover between groups; short duration |
| Holdout | Keep a random slice untreated during a roll-out | Treatment goes to everyone eventually | Ethics or revenue cost of withholding |
| Regression with controls | Compare units alike on measured traits | Everything that drives both treatment and outcome is measured | Unmeasured drivers still bias the result |
| Matching or weighting | Pair each treated unit with similar untreated ones | As above, with many traits to balance | Same as regression: only measured traits are matched |
| Difference-in-differences | Compare the change over time in a treated group with the change in an untreated group | A comparison group that would have moved in parallel without the treatment | Groups on different trends; events that hit only one group |
| Cut-off rule (regression discontinuity) | Compare units just above and just below an eligibility cut-off | A sharp rule, and units cannot steer themselves across the line | The effect is local to the cut-off |
| Natural experiment or instrument | Use something that shifts treatment but affects the outcome only through it | A credible source of as-good-as-random variation | Finding one; weak instruments give noisy answers |
| Before and after only | Compare the same units over time | Almost never enough on its own | Anything else that changed at the same time |

**Choosing.** Ask first whether a randomised test or holdout is possible. If not, look for a rule, a staggered roll-out or a comparison group that gives a natural control. Regression with controls is the weakest of the options that use a comparison, and it is honest only when it names what could not be measured.

**Parallel trends check for difference-in-differences.** Plot the two groups over several periods before the treatment. If they move together before, the assumption is believable; if not, the estimate absorbs a difference in trend.

**Reading the result.** Whatever the design, state the population the effect applies to (everyone, the treated, units near a cut-off) and the period. Do not extend a local effect to units it was not measured on.
