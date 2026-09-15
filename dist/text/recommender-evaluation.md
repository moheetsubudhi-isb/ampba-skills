# recommender-evaluation

Use this skill when: Measure whether a recommender or ranking system is any good, offline and online. Use whenever someone asks how to evaluate or compare recommendation models; how to split interaction data (random, temporal, leave-one-out) without leaking the future; whether to use RMSE or ranking metrics; how to compute precision@k, recall@k, hit rate, MAP, MRR or NDCG; how to check catalogue coverage, diversity, novelty, popularity bias or long-tail exposure; whether a new recommender beats the current one or a best-seller baseline; how to run a shadow deployment or A/B test for recommendations; or how many users that experiment needs to detect a lift. Also use for judging search-result ranking quality. Not for building the recommender, and not for setting a classifier's probability threshold.

# Recommender evaluation

Act as the data scientist who proves whether a recommender works, and as the advisor who says plainly whether it is worth shipping. Offline metrics only matter if they predict what customers do on the live site.

## Get the context that changes the answer

If recommendation logs, interaction data, model outputs or a current dashboard are available, look at them first: how many users and items, interactions per user, and the time span.

Then ask only what that material cannot answer, and only if the answer would change the evaluation. Ask at most three questions. Give each one a one-line reason and a default. If the request is urgent, run a first evaluation on stated assumptions and list the questions that would sharpen it.

The questions that usually matter here:

1. **Which user action counts as success?** A click, add-to-cart, purchase or finished watch. This defines relevance, and a click-optimised model can hurt purchases.
2. **How many items are shown, and does order matter on screen?** This sets k, and decides whether order-aware metrics are needed.
3. **What is the comparison, and is live traffic available?** The current system, a best-seller list, or nothing yet. This decides the baseline and whether an A/B test is possible.

If there is no answer, assume purchases define relevance, ten items are shown in ranked order, a best-seller baseline, and a temporal offline test followed by an A/B test.

## Procedure

Where a step names a script and code cannot run here, do the same check by hand on a small case, and say in the deliverable that it was done by hand.

1. **Define relevance** from real actions taken after the moment of recommendation. Use graded relevance when actions differ in strength, such as purchase 3, add-to-cart 2, click 1.
2. **Split the data the way production works.**
   - **Temporal split** by default: train before a cut-off date, test after it. Repeat over several cut-offs.
   - **Leave-last-n-out** per user for next-item recommendations.
   - **Random split** only for tastes that do not change over time, and say that it leaks the future otherwise.
3. **Set baselines:** best sellers overall, best sellers in the user's recent categories, and "buy again". A model that cannot beat them is not ready.
4. **Choose metrics that match the screen.**
   - **RMSE or MAE** only when predicted ratings are shown to users.
   - **Precision@k:** share of the k shown items that were relevant. Can be measured online.
   - **Recall@k:** share of the user's relevant items that appear in the top k. Offline only, because it needs the full relevant set.
   - **Hit rate@k and MRR** when one right item is enough.
   - **MAP@k** when order matters and relevance is yes or no; **NDCG@k** when order matters and relevance is graded.

   Average per user, then across users, so heavy users do not dominate. Report new and heavy users separately. `scripts/ranking_metrics.py` computes these from recommendation and truth files.
5. **Look beyond accuracy:** catalogue coverage, the share of recommendations taken by the top few percent of items, diversity within each list, novelty, and how often the same items repeat.
6. **Test online.**
   - **Shadow deployment** first: log what the new model would show, and check latency, errors and overlap with the current system.
   - **A/B test** next: randomise within strata such as region, device and tenure, check that groups are balanced before treatment, fix the primary metric and guardrails (revenue, returns, latency) in advance, and size the test with `scripts/ranking_metrics.py --sample-size`.
7. **Decide:** ship, iterate or stop, and state the trade-off accepted, for example slightly lower precision for much wider coverage.

## Deliverable

**Part A: Evaluation brief**, for the decision owner

- The verdict: ship, iterate or stop, with the single reason.
- The headline metric against the baseline, with its uncertainty.
- The trade-offs, and the online test plan with its sample size and duration.

**Part B: Technical appendix**, for the builders

- The split design and the relevance definition.
- A metric table per model and user segment.
- The experiment specification: strata, metrics, guardrails, stopping rule.

## Traps

- A random split that lets the model learn from the future.
- No baseline: a best-seller list often wins on precision.
- Recall@k reported from live data, where the full relevant set is unknown.
- Pooling all recommendations so heavy users decide the score.
- Evaluating only on candidates the model generated, which hides the items it never considered.
- Peeking at an A/B test daily and stopping at the first good day.
- Chasing NDCG until every user sees the same ten best sellers.
