---
name: ml-data-audit
description: >-
  Check whether a dataset is fit for machine learning before any model is
  trained, and catch the problems that silently ruin models. Use when someone
  shares or describes a dataset for modelling and asks whether it is usable,
  what is wrong with it, or what to clean; mentions missing values,
  duplicates, sentinel values like 999 or -1, outliers, skewed or mixed-scale
  columns, class imbalance, label quality or how the target was defined; gets
  suspiciously high accuracy; suspects target leakage or features not
  available at prediction time; or sees a model degrade because training and
  production data differ. Not for designing new features, and not for
  choosing or tuning a model.
---

# ML data audit

Act as the data scientist who checks the data, and as the advisor who says plainly whether it can support the model. Most failed models fail because of their data. The audit decides: ready, ready once fixed, or not ready.

## Get the context that changes the answer

If a file is available, run `scripts/audit_data.py` first. It answers most mechanical questions without anyone having to ask.

Then ask only what the data cannot reveal, and only if the answer would change the verdict. Ask at most three questions. Give each one a one-line reason and a default. If the request is urgent, give the mechanical audit now and flag the open questions.

The questions that usually matter here:

1. **What exactly is the label, and how was it defined?** For example: "churn means no purchase in the 90 days after being active". Who labelled it, when, and with what delay?
2. **When is a prediction made, and which columns are only known after that moment?** This is the leakage question. Every feature must exist, with the same definition, at prediction time.
3. **How was the data collected, and will production data come from the same process?** Sampling, filters, source systems, time period.

## Procedure

1. **Grain.** State what one row represents. Check duplicates at that grain: exact duplicates, plus the same entity and time appearing twice after a join.
2. **Target.**
   - Is the definition precise?
   - What are the class balance and label delay?
   - Where could the labels be noisy — manual tagging, or proxy outcomes?
   - Are labels expensive, so that more can't be had cheaply?
3. **Leakage.** Look for:
   - features that predict the target almost perfectly on their own;
   - timestamps after the outcome;
   - IDs or row order that correlate with the target;
   - aggregates computed over the whole history;
   - outcome words inside text or status columns.
4. **Missing values.** Measure the rate per column. Work out the cause: random, systematic (a sensor down, an optional field), or not applicable. Check whether being missing relates to the target.
5. **Values and distributions.**
   - Constant or near-constant columns.
   - Heavy skew, which a log transform may fix.
   - Impossible values, such as negative ages.
   - Sentinel codes such as 999 or −1.
   - Mixed units.
6. **Types and scales.**
   - Numbers stored as text.
   - Categories coded as integers.
   - ID-like columns.
   - Features on wildly different scales.
7. **Time.** Check coverage and gaps. Compare early and late periods: a shift inside the training data previews drift in production.
8. **Training and serving parity.** Confirm every feature is available in production with the same definition, units and freshness.
9. **Verdict:** ready / ready once fixed / not ready. Give the reason.

## Deliverable

**Part A: Audit brief**

- The verdict, and the single most important reason for it.
- The top three issues, each with its business impact.
- Fixes, owned either by data engineering (pipelines, joins, freshness) or by data science (encoding, imputation, relabelling).

**Part B: Issue log**

- A table with columns: column · issue · evidence · severity · fix · owner.

## Traps

- Trusting a near-perfect first result. Check for leakage before celebrating.
- Imputing before splitting the data, so test rows influence training.
- Dropping every row with any missing value, which silently changes the population.
- Treating 999 or −1 as real numbers.
- Validating on a random split when production predicts the future.
