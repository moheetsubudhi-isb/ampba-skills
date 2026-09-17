# value-of-information

Use this skill when: Decide whether to buy information before a decision: a market test, pilot, survey, trial run, inspection, diagnostic, consultant report or extra data. Use whenever someone asks whether a test or study is worth its cost; the most they should pay for research, a pilot or better data; the expected value of perfect information (EVPI) or of sample information (EVSI); how an imperfect test with false positives and false negatives should update the odds; why a positive result from an accurate test can still mean the event is unlikely (base rates, Bayes' rule); or whether to decide now or wait and learn. Not for building the decision tree for a choice with no test on offer, not for A/B test sample size or significance, and not for designing the survey questionnaire itself.

# Value of information

Act as the decision analyst who prices information, and as the advisor who says plainly when a study is not worth buying. Information has value only if it could change the decision.

## Get the context that changes the answer

If a business case, a decision tree or a quote for the study is available, look at it first: the options, the uncertain outcome the study would reveal, the payoffs, and the study's cost and track record.

Then ask only what that material cannot answer, and only if the answer would change the valuation. Ask at most three questions. Give each one a one-line reason and a default. If the request is urgent, give a first valuation on stated assumptions and list the questions that would sharpen it.

The questions that usually matter here:

1. **How accurate is the study?** Its hit rate when the outcome is good, and its false-alarm rate when it is bad. Without this, only the upper limit (EVPI) can be given.
2. **What does it cost, including the delay?** Waiting can lose a market window.
3. **Which decision would each result lead to?** If every result leads to the same choice, the study is worth nothing.

If there is no answer, compute EVPI as the ceiling, assume the business is risk-neutral, and treat delay as free.

## Procedure

Where a step names a script and code cannot run here, do the same check by hand on a small case, and say in the deliverable that it was done by hand.

1. **Value the decision without information.** The best EMV using prior probabilities (the decision-tree-analysis skill builds this).
2. **Find the ceiling (EVPI).** Assume a free, perfect forecast: for each outcome, take the best option's payoff, then weight by the prior. EVPI = that expected value − the best EMV without information. No study is worth more than EVPI. If EVPI is below the study's cost, stop: do not buy it.
3. **Turn the study's accuracy into updated probabilities** with Bayes' rule:
   - P(result) = Σ P(result | outcome) × P(outcome).
   - P(outcome | result) = P(result | outcome) × P(outcome) / P(result).
   When the outcome is rare, even an accurate test gives many false positives; show the numbers.
4. **Value the imperfect study (EVSI).** For each possible result, find the best option using the updated probabilities, weight by P(result), then subtract the EMV without information. EVSI is always between 0 and EVPI.
5. **Decide.** Buy the study if EVSI exceeds its full cost. Report efficiency = EVSI / EVPI as a measure of how close the study comes to perfect.
6. **Run everything** with `scripts/info_value.py`: payoffs, priors and the study's likelihoods in, EVPI, EVSI, updated probabilities and the decision rule for each result out.
7. **Check sensitivity** to the prior and to the study's accuracy; a study is often worth buying only within a narrow band of priors.

## Deliverable

**Part A: Information brief**, for the decision owner

- Buy or skip the study, and the most worth paying for it.
- What to do on each possible result.
- How much the answer depends on the prior and on the study's accuracy.

**Part B: Analysis appendix**, for the analysts

- The payoff table, priors and likelihoods.
- Updated probabilities for each result.
- EVPI, EVSI and efficiency, with the working.

## Traps

- Paying for a study whose every result leads to the same decision.
- Paying more than EVPI for any study.
- Confusing P(positive result | good outcome) with P(good outcome | positive result).
- Ignoring the base rate, so a positive test on a rare event is over-trusted.
- Leaving out the cost of delay.
- Taking a vendor's claimed accuracy without asking how it was measured.
