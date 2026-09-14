# feature-engineering

Use this skill when: Design, transform and debug model features so the model learns the signal that matters. Use when someone asks what features to build; how to encode categorical variables or high-cardinality IDs; how to handle dates, times, text, locations or event histories; how to create ratios, lags, rolling windows or per-customer aggregates without leaking the future; how to log-transform or scale skewed columns, impute missing values or pick defaults; whether target encoding is safe; or when a model underperforms, looks strangely complex, or misbehaves on certain inputs and a feature may be the cause. Not for auditing whether a dataset is usable at all, and not for reducing many existing columns to fewer.

# Feature engineering

Act as the data scientist designing features and as the advisor who keeps them honest. A good feature carries what an expert would look at, is available at prediction time, and means the same thing in training and in production.

## Get the context that changes the answer

If data or a schema is available, look at it first. Check columns, types, timestamps and the grain of each table.

Then ask only what the data and the request cannot answer, and only if the answer would change which features you build. Ask at most three questions. Give each one a one-line reason and a default. If the request is urgent, give a first set of ideas on stated assumptions.

The questions that usually matter here:

1. **When is the prediction made, and what information exists at that moment?** This sets the leakage boundary. Anything recorded after that moment cannot be a feature.
2. **Which model family is planned?** Tree models need little scaling and handle raw categories better. Linear and distance-based models need scaling and careful encoding.
3. **What does an expert look at to judge a case by eye?** This is the richest source of features.

## Procedure

1. **Start from the prediction moment.** List what is known at that time, and at what freshness. Mark every candidate column as available or not available when the prediction is made.
2. **Choose the mindset deliberately.**
   - *Model-centric:* throw every raw feature in and let a complex model find patterns. It needs lots of data and explains poorly.
   - *Feature-centric:* craft features from domain knowledge and use a simpler model. It needs less data and explains well.
   - Complexity is conserved: whatever the features don't carry, the model must learn. Recommend based on data volume and explainability needs.
3. **Turn raw events into what an expert reasons with.** Example: from two card transactions' time and location, derive the distance between them and the time gap, then the implied travel speed. An impossible speed flags fraud better than any raw column.
4. **Model the variance that matters.** Divide raw measures by whatever inflates them: per visit, per active day, per unit of length, per capita. Rates and ratios generalise; raw totals often just track size.
5. **Encode by model family.** Load `references/encoding.md`.
6. **Build time and history features with point-in-time correctness.** Load `references/time-and-history.md`.
7. **Handle missing values and defaults on purpose.**
   - Ask why a value is missing: a sensor failure, an optional field, not applicable, or never happened.
   - Missingness is often signal, so add an indicator column.
   - Choose defaults that mean the right thing. "Days since last complaint" for a customer who never complained must not be 0, because that reads as "complained today". Use a large value plus a never-complained flag.
8. **Transform the shape.** Use `log1p` for heavy-tailed amounts and counts. Standardise or min-max scale for linear and distance-based models.
9. **Treat an oddly complex model as a symptom.** Very deep trees, huge coefficients, or many interactions often mean the model is compensating for a feature bug: a wrong default, mixed units, or duplicated rows from a join.
10. **Prove the value of each feature group.** Compare cross-validated scores with and without the group. Fit every encoder, scaler and imputer inside the cross-validation pipeline, never on the full data.

## Deliverable

**Part A: Brief**

- The top feature ideas, ranked by expected value and build cost.
- The data engineering each one needs: joins, windows, freshness, backfills.
- Risks: leakage, and features unavailable at serving time.

**Part B: Feature specification**

- A table with columns: name · definition · source · window · available at prediction time? · transform · owner.
- Pipeline code showing that transforms are fitted on training folds only.

## Traps

- Aggregates computed over the whole history, including the period after the prediction date.
- Target encoding fitted on the full data, not out-of-fold.
- Defaults that read as real values, such as 0 for "never happened".
- The same feature computed differently in the training batch and the live service.
- Label or outcome information hidden inside free text or status columns.
- One-hot encoding thousands of levels for a linear model.

---

## Reference: references/encoding.md

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

---

## Reference: references/time-and-history.md

# Time and history features

**Point-in-time rule:** for each training row, compute every feature using only events before that row's prediction time. This is the most common source of leakage in production models.

**Calendar**
- Hour and weekday as cyclical pairs: `sin(2*pi*hour/24)`, `cos(2*pi*hour/24)`.
- Holiday, festival, payday and month-end flags for the relevant region.
- Business-specific calendars, such as sale events or school terms.

**Recency, frequency, monetary, per entity**
- Days since the last event (with the never-happened rule: a large value plus a flag).
- Event count in the last 7, 30 and 90 days.
- Sum and mean of amounts over the same windows.
- Trend: last 30 days divided by the previous 30.

**Sequences**
- Time gap between consecutive events. Its mean and variance show regularity.
- Share of events of each type within a window.
- Change from the entity's own normal, such as "spend today ÷ median daily spend".

**Point-in-time joins with pandas**
```python
import pandas as pd
events = events.sort_values("event_time")
labels = labels.sort_values("prediction_time")
features = pd.merge_asof(labels, events, left_on="prediction_time", right_on="event_time",
                         by="customer_id", direction="backward", allow_exact_matches=False)
```

**Serving parity:** compute windows with the same code in the training batch and the live feature service, or store features in a feature store with event-time semantics. Log the served values and compare their distribution against training.
