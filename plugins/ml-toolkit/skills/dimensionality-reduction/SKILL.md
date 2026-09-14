---
name: dimensionality-reduction
description: >-
  Reduce many features to fewer, and choose between PCA, Fisher linear
  discriminant analysis, feature selection and 2-D visualisation methods. Use
  when a dataset has dozens or hundreds of correlated columns; when someone
  asks whether to use PCA, how many principal components to keep, or what the
  loadings mean; how to visualise high-dimensional data or embeddings; whether
  to use t-SNE or UMAP; how to remove noise or multicollinearity; when to use
  LDA to separate classes; or which features to keep or drop. Not for grouping
  records into segments, and not for creating new features from raw data.
---

# Dimensionality reduction

Act as the data scientist choosing the projection and as the advisor who explains what gets lost. Fewer dimensions buy speed, stability and pictures. The cost is explainability, and sometimes signal.

## Get the context that changes the answer

If data is available, look at it first. Count the columns, check their types, and look at the correlation structure and any label column.

Then ask only what the data and the request cannot answer, and only if the answer would change the method. Ask at most three questions. Give each one a one-line reason and a default. If the request is urgent, deliver a first cut on stated assumptions.

The questions that usually matter here:

1. **Are there class labels, and is the goal to separate those classes?** This is the question that routes the whole skill. PCA keeps the directions of greatest total variance, and those may have nothing to do with the classes. It can blur classes together. Fisher discriminant analysis looks for the directions that separate the classes.
2. **What is the reduced data for?** A picture, a faster or more stable downstream model, denoising, or explaining drivers to stakeholders?
3. **Must stakeholders see the original columns?** If they must, select features rather than build combinations of them.

## Choose the method, then load its reference

| Goal | Method | Load |
|---|---|---|
| Compress numeric features with no labels; keep the most information | PCA | `references/pca.md` |
| Separate known classes; a projection built for discrimination | Fisher / linear discriminant analysis | `references/fisher-lda.md` |
| Keep original, explainable columns | Feature selection | this file, below |
| A 2-D picture only | PCA first; t-SNE or UMAP for local neighbourhoods | this file, below |

## Procedure

1. **Scale numeric features.** Otherwise the column with the largest range dominates the first component.
2. **Split before fitting.** Fit the scaler and the reducer on training data only, inside a pipeline. Fitting on all the data leaks information from the test set.
3. **Apply the chosen method** using its reference.
4. **Measure what was kept and what was lost.** Run `scripts/projection_check.py`. It shows variance explained, how many components reach 80%, 90% and 95%, and the top loadings. With `--target`, it compares cross-validated accuracy after PCA with accuracy after LDA. That shows directly whether PCA threw away class signal.
5. **Decide by the downstream purpose,** not by a variance threshold alone. Keep the smallest number of dimensions whose downstream score sits within noise of the full-feature score.

## Feature selection (when original columns must stay)

- **Filter:** drop near-constant columns, and one of each pair correlated above about 0.9. Rank the rest by a score: Fisher score or mutual information for classification, correlation for regression.
- **Wrapper:** recursive feature elimination with cross-validation. Costly, but it accounts for how features interact.
- **Embedded:** L1-regularised linear models, or importance from tree models checked by permutation. Impurity-based importance favours high-cardinality columns.

## 2-D pictures

- Start with PCA's first two components. They are honest about global structure.
- t-SNE and UMAP show local neighbourhoods well, but distances between clusters, cluster sizes and gaps between groups are not meaningful. Try several perplexity or neighbour settings before trusting a pattern.
- Never feed t-SNE output to a model as features.

## Deliverable

**Part A: Brief**

- The recommended method and number of dimensions.
- How much information is kept, and the effect on the downstream model score.
- What becomes harder to explain, and what was deliberately dropped.

**Part B: Technical appendix**

- Variance table and top loadings per component.
- PCA-versus-LDA comparison, where labels exist.
- Pipeline code that fits on training data only.

## Traps

- No scaling before PCA.
- Fitting PCA on the full dataset before the train/test split.
- Naming components ("PC1 = affluence") without reading the loadings.
- Dropping low-variance components that carry the class signal.
- PCA on one-hot encoded categories.
- Reading t-SNE distances or cluster sizes literally.
