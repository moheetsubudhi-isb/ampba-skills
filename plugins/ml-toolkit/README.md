# Ml toolkit

Data-science skills for framing ML problems, auditing data, engineering features, reducing dimensions, clustering, model selection and validation, classification and regression metrics, tree ensembles, linear and logistic models, anomaly detection, and text embeddings.

Part of [Business Analytics Skills](https://github.com/moheetsubudhi-isb/business-analytics-skills), a set of agent skills that make an AI assistant work like a decision scientist and an advisor. Each skill asks what the work is for only when the answer would change the result, follows a real method step by step, runs a check wherever there is logic to verify, and hands back a plain-language brief plus a technical appendix.

## Skills (12)

- **anomaly-detection**: Find unusual transactions, sensor readings, log events, users or records, and choose the detection method: z-score or IQR rules, robust statistics, Mahalanobis distance, isolation forest, local….
- **classification-metrics-and-threshold**: Judge a classifier by what its errors cost, and set the decision threshold.
- **clustering-and-segmentation**: Group customers, products, stores, sessions or any records into segments, and pick the clustering method that fits the data and the business use.
- **dimensionality-reduction**: Reduce many features to fewer, and choose between PCA, Fisher linear discriminant analysis, feature selection and 2-D visualisation methods.
- **feature-engineering**: Design, transform and debug model features so the model learns the signal that matters.
- **linear-and-logistic-models**: Build, regularise and interpret linear regression, logistic regression and multinomial (softmax) models used for prediction.
- **ml-data-audit**: Check whether a dataset is fit for machine learning, and catch the problems that silently ruin models.
- **ml-problem-framing**: Decide whether, and how, machine learning should solve a business problem before any data work starts.
- **model-selection-and-validation**: Choose a model family, design validation that proves the model will generalise, and diagnose overfitting or underfitting.
- **regression-error-metrics**: Judge whether a regression or forecast model's errors are good enough, and choose the error metric the business should see: MAE, RMSE, MAPE, WAPE, R-squared, bias, or a cost-weighted error.
- **text-and-embedding-features**: Turn text into numbers for search, matching, deduplication, classification or clustering, and choose between TF-IDF, embeddings and simpler methods.
- **tree-and-ensemble-models**: Build, tune and explain decision trees and tree ensembles: random forest, bagging, AdaBoost, gradient boosting, XGBoost, LightGBM and CatBoost.

## Use

Skills load by themselves when a request matches. Ask a normal work question; to call one directly, type `/` and the skill name in Claude Code, Cursor or Copilot, or `$` and the name in Codex.

## What it runs

Instructions only, plus small optional Python checks (`scripts/`, standard library, numpy, pandas or scikit-learn) that read only the file you point them at. Nothing here reads credentials, environment secrets or your files on its own, makes network calls, or sends data anywhere.

## Licence

MIT. Source and issues: https://github.com/moheetsubudhi-isb/business-analytics-skills
