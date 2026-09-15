# Statistical anomaly rules

## z-score

z = (x − mean) / standard deviation. Flag |z| > 3, which is about 0.3% of a normal distribution.
- Simple and explainable.
- Assumes a roughly symmetric distribution. Extreme values inflate the mean and standard deviation, which hides them: a few huge transactions raise the standard deviation until none looks extreme.

## Robust z-score

Use the median and the median absolute deviation (MAD): z = 0.6745 × (x − median) / MAD. Flag above 3.5. Unaffected by the outliers themselves.

## IQR rule

Q1 and Q3 are the 25th and 75th percentiles; IQR = Q3 − Q1. Flag values below Q1 − 1.5 × IQR or above Q3 + 1.5 × IQR (3 × IQR for extreme outliers). No distribution assumption. On heavily skewed data, log-transform first or the upper fence flags normal large values.

## Mahalanobis distance

Distance from the centre that accounts for the correlation between features: D² = (x − μ)ᵀ Σ⁻¹ (x − μ). For roughly normal data with p features, D² follows a chi-squared distribution with p degrees of freedom, so a 99.9th-percentile cut-off is a reasonable start.
- Catches unusual combinations: a customer with an ordinary income and ordinary spend, but spend far too high for that income.
- Estimate μ and Σ robustly (minimum covariance determinant) when the data already contains outliers.
- Assumes one roughly elliptical cloud; for several groups, compute it within each group.

## Time series

1. Remove trend and seasonality: compare with the same hour last week, a rolling median, or a seasonal decomposition.
2. Apply robust z-scores or IQR rules to the residuals.
3. Require persistence (for example two consecutive points) to cut one-off noise, when a short delay is acceptable.
4. Keep separate baselines for weekdays, weekends and holidays.
