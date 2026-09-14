# Shortlisting models for tabular data

| Model | Strengths | Weaknesses | Reach for it when |
|---|---|---|---|
| Linear or logistic regression (L1/L2) | Explainable, fast, stable on small data, gives probabilities | Needs features for non-linear effects and interactions | Regulated or explainable decisions; a baseline; few rows |
| Decision tree (pruned) | Readable rules, handles mixed types and interactions | Unstable, overfits without depth limits | Rules are wanted; stakeholders want to see the logic |
| Random forest | Strong default, little tuning, robust | Larger, slower predictions, less explainable | A dependable first serious model |
| Gradient boosting (XGBoost, LightGBM, CatBoost) | Usually the best accuracy on tabular data | Needs tuning, overfits with too many rounds | Accuracy matters and there is data to tune on |
| k-nearest neighbours / Parzen window | No training step; local patterns | Slow predictions, needs scaling, weak in high dimensions | Small, low-dimensional data; similarity-based decisions |
| Naive Bayes / density-based classifiers | Fast, work with little data, give probabilities | Strong independence or shape assumptions | Text-like counts; quick baselines |
| Neural networks | Images, text, audio, very large data | Data-hungry, costly, hard to explain | Unstructured inputs |

**Complexity knobs**
- Tree: `max_depth`, `min_samples_leaf`, pruning `ccp_alpha`.
- KNN: `k` (larger k is simpler); Parzen: bandwidth (wider is simpler).
- Linear models: regularisation strength (`C` smaller, or `alpha` larger, is simpler).
- Boosting: `learning_rate` × `n_estimators`, `max_depth`, and subsampling.
