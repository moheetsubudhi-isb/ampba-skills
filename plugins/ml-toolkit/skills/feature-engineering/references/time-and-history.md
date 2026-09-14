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
