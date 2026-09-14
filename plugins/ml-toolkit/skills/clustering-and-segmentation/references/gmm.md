# Gaussian mixture models

**Use when** groups overlap, clusters are elliptical rather than round, or the business needs membership probabilities — for example, "70% likely to be a bargain hunter".

**Procedure**
1. Scale the columns.
2. Fit k from 1 to about 10 with `n_init` of at least 3. Choose k by the lowest BIC.
3. Choose the covariance type:
   - `full`: flexible ellipses, many parameters;
   - `diag`: axis-aligned ellipses;
   - `spherical`: behaves like k-means.
   Compare BIC across types.
4. Use `predict_proba` for soft membership. Flag records with no component above about 0.6 as mixed.

**Limits**
Sensitive to initialisation, so use several starts. With too few rows per component, full covariance overfits. It assumes each group is roughly Gaussian, so log-transform skewed columns first.
