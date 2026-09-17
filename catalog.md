# Catalog

One skill per moment. When a later module covers the same moment, it improves the existing skill rather than adding a new one.

| Skill | Moment it handles | Toolkit | Source modules | Trigger eval | Status |
|---|---|---|---|---|---|
| `optimization-formulation` | Turning a business decision into a model and a recommendation; judging whether extra capacity is worth paying for | optimization | T1-OPT S1, S3, S5 | 20/20 | pilot |
| `logical-constraints` | Writing yes/no business rules as correct MIP constraints, with proof | optimization | T1-OPT S3 | 20/20 | pilot |
| `shortage-allocation-fairness` | Too little supply for the demand; choosing and pricing a definition of fair | optimization | T1-OPT S1, S3 | 20/20 | pilot |
| `exact-vs-heuristic` | A solver too slow for the real problem size; setting expectations on speed and quality | optimization | T1-OPT S4 | 20/20 | pilot |
| `or-model-test-plan` | Deciding whether a model's plans can be trusted before go-live | optimization | T1-OPT S2, S5 | 20/20 | pilot |
| `ml-problem-framing` | Deciding whether and how ML should solve a problem; target, labels, baseline, metric chain | ml | T1-MLUL D1, T2-MLSL1 L1-L2, L4, T3-MLSL2 | 20/20 | tier 1 |
| `ml-data-audit` | Deciding whether a dataset can support a model; leakage, label definition, train/serve parity | ml | T2-MLSL1 L2 | 20/20 | tier 1 |
| `feature-engineering` | Designing and debugging features with point-in-time correctness | ml | T2-MLSL1 L6, T1-MLUL D1 | 20/20 | tier 1 |
| `dimensionality-reduction` | Too many features; PCA vs Fisher/LDA vs feature selection vs 2-D pictures | ml | T2-MLSL1 L3, L5, L10 | 20/20 | tier 1 |
| `clustering-and-segmentation` | Segmenting records; choosing k-means, hierarchical, DBSCAN, GMM or mixed-type methods | ml | T1-MLUL D1-D4 | 20/20 | tier 1 |
| `model-selection-and-validation` | Choosing a model and a split that proves generalisation; bias-variance, tuning | ml | T3-MLSL2, T2-MLSL1 L4, L7-L9 | 20/20 | tier 1 |
| `classification-metrics-and-threshold` | Judging a classifier by error costs and setting the threshold | ml | T3-MLSL2, T2-MLUL2 D3 | 20/20 | tier 1 |
| `tree-and-ensemble-models` | Choosing, tuning and explaining a tree, random forest or boosted model | ml | T3-MLSL2, T2-MLSL1 L8 | 20/20 | tier 2 |
| `linear-and-logistic-models` | Regularising and reading linear, logistic and softmax models built for prediction | ml | T3-MLSL2, T2-MLSL1 L9 | 20/20 | tier 2 |
| `regression-error-metrics` | Judging regression and forecast errors against a baseline and the cost of acting on them | ml | T3-MLSL2 | 20/20 | tier 2 |
| `anomaly-detection` | Finding unusual records with few labels, and setting alert volume from review capacity | ml | T2-MLUL2 D5, T2-MLSL1 L10 | 20/20 | tier 2 |
| `text-and-embedding-features` | Representing text for matching, deduplication and search; TF-IDF or embeddings | ml | T1-MLUL D4 | 20/20 | tier 2 |
| `recommender-build` | Choosing and building association rules, collaborative filtering, matrix factorisation or graph ranking | recommender | T2-MLUL2 D1, D2, D4 | 20/20 | new |
| `recommender-evaluation` | Proving a recommender works offline and online: splits, ranking metrics, A/B sizing | recommender | T2-MLUL2 D3 | 20/20 | new |
| `datastore-selection` | Deciding where each kind of data should live: relational, columnar, document, key-value, graph, lake | data-engineering | T1-DE S1-S4 | 20/20 | new |
| `distribution-key-and-partitioning` | Laying out distribution keys, partitions and shard keys; fixing skew and data movement | data-engineering | T1-DE S2, MPP note | 20/20 | new |
| `pipeline-and-quality-design` | Designing ETL/ELT flows, medallion layers, data contracts, quality checks, reconciliation and governance | data-engineering | T1-DE S1, S4, S5 | 20/20 | new |
| `spark-job-design-and-review` | Reviewing and speeding up a Spark job: shuffles, caching, partitions, joins, driver memory | data-engineering | T3-BDM | pending | new |
| `cluster-storage-and-sizing` | Sizing HDFS disk, nodes and NameNode memory; small files; cluster vs object storage | data-engineering | T3-BDM | pending | new |
| `price-elasticity-estimation` | Measuring how sales respond to price and promotions, and whether a price move or deal pays | pricing | T3-PDA | pending | new |
| `willingness-to-pay-research` | Designing willingness-to-pay research and setting prices from it | pricing | T3-PDA | pending | new |
| `pricing-structure-design` | Segment prices, tiers, fences, bundles and product-line ladders that hold up | pricing | T3-PDA | pending | new |
| `decision-tree-analysis` | Structuring a choice under uncertainty by EMV, with sensitivity and risk | decision-analysis | T3-AOS | pending | new |
| `value-of-information` | Deciding whether a test, survey or pilot is worth buying: EVPI, EVSI, Bayes | decision-analysis | T3-AOS | pending | new |
| `simulation-model-design` | Monte Carlo risk models: distributions, run counts, newsvendor orders, schedule risk | decision-analysis | T3-AOS | pending | new |

Trigger evals use `tools/trigger_eval.py`: 10 queries that should fire the skill and 10 that should not, with the negatives taken from sibling skills so overlaps surface. One run per query; runs that time out are retried with a longer limit rather than scored as failures.

Overlaps found and fixed this way: `optimization-formulation` was taking shortage and solver-too-slow questions from its siblings, and `shortage-allocation-fairness` was taking model-testing questions. Both descriptions now say what they are not for. In the ML toolkit, `model-selection-and-validation` fired on a bare definition question ("What is cross-validation?"), and `ml-data-audit` stayed silent on direct leakage and prediction-time availability questions; the first now excludes definitions with no dataset or model in play, and the second leads with those phrasings and applies even before the data is shared.

The second wave (data engineering, recommenders and the ML model families) reached 20/20 the same way. `linear-and-logistic-models` first missed plain-language questions such as what an odds ratio means; leading its description with those pulled them in but then caught "What is linear regression?", which a definition scope-out settled.
