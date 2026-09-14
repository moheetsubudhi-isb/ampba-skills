# Validation design

| Data situation | Split | scikit-learn |
|---|---|---|
| Independent rows, balanced target | K-fold, shuffled | `KFold(5, shuffle=True)` |
| Independent rows, imbalanced classes | Stratified k-fold | `StratifiedKFold` |
| Repeated entities (customers, patients, stores) | Group k-fold: each entity sits entirely in one fold | `GroupKFold`, `StratifiedGroupKFold` |
| Predicting the future from the past | Forward-chaining, rolling-origin validation | `TimeSeriesSplit`, with a gap if labels mature slowly |
| New entities *and* future periods | Split by time, and exclude training entities from the validation period | Custom split |
| Small data (a few hundred rows) | Repeated stratified k-fold, and report the spread | `RepeatedStratifiedKFold` |

**Rules**
- Hold out a final test set that matches the production situation, such as the most recent period. Touch it once.
- Tuning and reporting on the same folds inflates the score. Use nested cross-validation, or a separate hold-out.
- Label maturity: if outcomes take 60 days to be known, leave a 60-day gap between the end of training and the start of validation.
- Mirror production: if the model is retrained monthly and predicts the next month, validate exactly that way.
