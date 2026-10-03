# Catalog

One skill per decision moment. When a new topic covers a moment that already has a skill, it improves that skill rather than adding a second one.

The **trigger eval** column is how reliably a skill fires on the questions it should, and stays quiet on the ones it should not. See the note under the table.

| Skill | Moment it handles | Toolkit | Trigger eval | Status |
|---|---|---|---|---|
| `optimization-formulation` | Turning a business decision into a model and a recommendation; judging whether extra capacity is worth paying for | optimization | 20/20 | pilot |
| `logical-constraints` | Writing yes/no business rules as correct MIP constraints, with proof | optimization | 20/20 | pilot |
| `shortage-allocation-fairness` | Too little supply for the demand; choosing and pricing a definition of fair | optimization | 20/20 | pilot |
| `exact-vs-heuristic` | A solver too slow for the real problem size; setting expectations on speed and quality | optimization | 20/20 | pilot |
| `or-model-test-plan` | Deciding whether a model's plans can be trusted before go-live | optimization | 20/20 | pilot |
| `ml-problem-framing` | Deciding whether and how ML should solve a problem; target, labels, baseline, metric chain | ml | 20/20 | tier 1 |
| `ml-data-audit` | Deciding whether a dataset can support a model; leakage, label definition, train/serve parity | ml | 20/20 | tier 1 |
| `feature-engineering` | Designing and debugging features with point-in-time correctness | ml | 20/20 | tier 1 |
| `dimensionality-reduction` | Too many features; PCA vs Fisher/LDA vs feature selection vs 2-D pictures | ml | 20/20 | tier 1 |
| `clustering-and-segmentation` | Segmenting records; choosing k-means, hierarchical, DBSCAN, GMM or mixed-type methods | ml | 20/20 | tier 1 |
| `model-selection-and-validation` | Choosing a model and a split that proves generalisation; bias-variance, tuning | ml | 20/20 | tier 1 |
| `classification-metrics-and-threshold` | Judging a classifier by error costs and setting the threshold | ml | 20/20 | tier 1 |
| `tree-and-ensemble-models` | Choosing, tuning and explaining a tree, random forest or boosted model | ml | 20/20 | tier 2 |
| `linear-and-logistic-models` | Regularising and reading linear, logistic and softmax models built for prediction | ml | 20/20 | tier 2 |
| `regression-error-metrics` | Judging regression and forecast errors against a baseline and the cost of acting on them | ml | 19/20 | tier 2 |
| `anomaly-detection` | Finding unusual records with few labels, and setting alert volume from review capacity | ml | 20/20 | tier 2 |
| `text-and-embedding-features` | Representing text for matching, deduplication and search; TF-IDF or embeddings | ml | 20/20 | tier 2 |
| `recommender-build` | Choosing and building association rules, collaborative filtering, matrix factorisation or graph ranking | recommender | 20/20 | new |
| `recommender-evaluation` | Proving a recommender works offline and online: splits, ranking metrics, A/B sizing | recommender | 19/20 | new |
| `datastore-selection` | Deciding where each kind of data should live: relational, columnar, document, key-value, graph, lake | data-engineering | 20/20 | new |
| `distribution-key-and-partitioning` | Laying out distribution keys, partitions and shard keys; fixing skew and data movement | data-engineering | 20/20 | new |
| `pipeline-and-quality-design` | Designing ETL/ELT flows, medallion layers, data contracts, quality checks, reconciliation and governance | data-engineering | 20/20 | new |
| `price-elasticity-estimation` | Measuring how sales respond to price and promotions, and whether a price move or deal pays | pricing | 20/20 | new |
| `willingness-to-pay-research` | Designing willingness-to-pay research and setting prices from it | pricing | 19/20 | new |
| `pricing-structure-design` | Segment prices, tiers, fences, bundles and product-line ladders that hold up | pricing | 20/20 | new |
| `decision-tree-analysis` | Structuring a choice under uncertainty by EMV, with sensitivity and risk | decision-analysis | 20/20 | new |
| `value-of-information` | Deciding whether a test, survey or pilot is worth buying: EVPI, EVSI, Bayes | decision-analysis | 20/20 | new |
| `simulation-model-design` | Monte Carlo risk models: distributions, run counts, newsvendor orders, schedule risk | decision-analysis | 19/20 | new |
| `experiment-design-and-readout` | Sizing, running and reading a randomised test; stopping rules, split checks, guardrails | statistics | 20/20 | new |
| `group-difference-test` | Is this difference between two groups, or before and after, real? Paired vs independent, size of the gap | statistics | 19/20 | new |
| `estimate-with-margin-of-error` | What a sample says about the whole population, and how big a sample to take | statistics | 20/20 | new |
| `control-limits-and-error-costs` | Setting alert, control and pass/fail limits from the cost of false alarms and misses | statistics | 20/20 | new |
| `causal-claim-check` | Did X cause Y? Selection bias, what to control for, when an experiment is needed | statistics | 20/20 | new |
| `regression-diagnostics` | Can this regression be trusted for inference? Output table, residuals, influence, unequal variance | statistics | 17/20 | new |
| `prediction-interval-reporting` | An honest range around one prediction, and whether the range really covers | statistics | 20/20 | new |
| `count-and-rate-models` | Counts and rates: Poisson, offsets, overdispersion, negative binomial, excess zeros | statistics | 20/20 | new |
Trigger evals use `tools/trigger_eval.py`: 10 queries that should fire the skill and 10 that should not, with the negatives taken from sibling skills so overlaps surface. One run per query; runs that time out are retried with a longer limit rather than scored as failures.

Overlaps found and fixed this way: `optimization-formulation` was taking shortage and solver-too-slow questions from its siblings, and `shortage-allocation-fairness` was taking model-testing questions. Both descriptions now say what they are not for. In the ML toolkit, `model-selection-and-validation` fired on a bare definition question ("What is cross-validation?"), and `ml-data-audit` stayed silent on direct leakage and prediction-time availability questions; the first now excludes definitions with no dataset or model in play, and the second leads with those phrasings and applies even before the data is shared.

The second group (data engineering, recommenders and the ML model families) reached 20/20 the same way. `linear-and-logistic-models` first missed plain-language questions such as what an odds ratio means; leading its description with those pulled them in but then caught "What is linear regression?", which a definition scope-out settled.

The pricing and decision-analysis skills were scored after fixing wording misses. `decision-tree-analysis` first missed plain "should we launch?" questions until its description led with them. `pricing-structure-design` missed price-ladder, discount-erosion, volume-discount and pricing-fairness questions until those moved to the front. Two skills keep one borderline miss each: `willingness-to-pay-research` on "here are 400 survey responses with the most each would pay; what price maximises revenue?", and `simulation-model-design` on a bare newsvendor critical-ratio calculation. Two big-data skills (Spark job review and HDFS cluster sizing) were built and then dropped, because few users run Spark or Hadoop themselves; the everyday parts of that topic live in `distribution-key-and-partitioning`, `datastore-selection` and `pipeline-and-quality-design`.

The statistics group adds eight skills split by decision moment instead of one general statistics skill. The local prototype `regression-sanity-check` competed with `causal-claim-check` for the same questions and is retired by it. Overlaps were settled this way: multicollinearity and VIF stay with `linear-and-logistic-models`, so `regression-diagnostics` scopes them out; `regression-diagnostics` now takes residual-plot questions about price predictions that `regression-error-metrics` used to take, and `experiment-design-and-readout` takes A/B sample-size questions for click-through that `recommender-evaluation` used to take, which leaves each of those older skills at 19/20. `regression-diagnostics` keeps three misses on short questions with no model in play: whether to use robust standard errors, whether a model with adjusted R-squared 0.20 and a significant F test is good, and whether repeated customers break standard errors. `group-difference-test` keeps one: app versus web spend with data attached, which is often answered directly.

The eval harness now stops each run as soon as the verdict is known, and counts a run that ends in an error, such as a usage limit, as unknown rather than as a miss. Several earlier rounds had scored limit failures as misses.

