# Encoding categorical features

| Situation | Encoding | Notes |
|---|---|---|
| Few levels (under about 15), any model | One-hot | Drop one level only for unregularised linear models |
| Natural order, such as size S/M/L or rating bands | Ordinal integers | Only when the order is real |
| Many levels, tree models | Native categorical support (LightGBM, CatBoost, sklearn `HistGradientBoosting`) or frequency encoding | Group rare levels first |
| Many levels, linear models | Out-of-fold target encoding with smoothing, or hashing | Never fit target encoding on the full data |
| Very high cardinality or unseen levels in production | Hashing, or an "other" bucket | Decide how unseen levels are handled at serving time |
| Text-like categories, such as product titles | See the text section of the feature-engineering skill | |

**Rare levels:** group levels below about 1% of rows, or below a minimum count, into "other". Do this on training data only.

**Target encoding done safely**
1. Within each training fold, compute each level's target mean on the other folds.
2. Shrink toward the global mean: `(count * level_mean + m * global_mean) / (count + m)`, with `m` around 10–100.
3. Fit the final mapping on all training data, and apply it to test and production data.

**Pipeline pattern (scikit-learn)**
```python
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler, TargetEncoder
from sklearn.impute import SimpleImputer

pre = ColumnTransformer([
    ("num", make_pipeline(SimpleImputer(strategy="median", add_indicator=True), StandardScaler()), numeric_cols),
    ("low_card", OneHotEncoder(handle_unknown="infrequent_if_exist", min_frequency=0.01), low_card_cols),
    ("high_card", TargetEncoder(smooth="auto"), high_card_cols),  # cross-fitted internally
])
model = make_pipeline(pre, estimator)  # cross-validate the whole pipeline
```
