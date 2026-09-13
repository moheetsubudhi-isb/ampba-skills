# Catalog

One skill per moment. When a later module covers the same moment, it improves the existing skill rather than adding a new one.

| Skill | Moment it handles | Toolkit | Source modules | Trigger eval | Status |
|---|---|---|---|---|---|
| `optimization-formulation` | Turning a business decision into a model and a recommendation; judging whether extra capacity is worth paying for | optimization | T1-OPT S1, S3, S5 | 20/20 | pilot |
| `logical-constraints` | Writing yes/no business rules as correct MIP constraints, with proof | optimization | T1-OPT S3 | 20/20 | pilot |
| `shortage-allocation-fairness` | Too little supply for the demand; choosing and pricing a definition of fair | optimization | T1-OPT S1, S3 | 20/20 | pilot |
| `exact-vs-heuristic` | A solver too slow for the real problem size; setting expectations on speed and quality | optimization | T1-OPT S4 | 20/20 | pilot |
| `or-model-test-plan` | Deciding whether a model's plans can be trusted before go-live | optimization | T1-OPT S2, S5 | 20/20 | pilot |

Trigger evals use `tools/trigger_eval.py`: 10 queries that should fire the skill and 10 that should not, with the negatives taken from sibling skills so overlaps surface. One run per query; runs that time out are retried with a longer limit rather than scored as failures.

Two overlaps found and fixed this way: `optimization-formulation` was taking shortage and solver-too-slow questions from its siblings, and `shortage-allocation-fairness` was taking model-testing questions. Both descriptions now say what they are not for.
