# Principal components analysis

**Use when** the data is numeric and multivariate, there are many features, labels are absent or ignored, and the goal is to visualise, compress for later stages, or remove noise.

**Idea**
Find orthogonal directions in decreasing order of variance. The first direction keeps the most variance; each later one keeps the most of what remains. Large eigenvalues are structure; the long tail of small ones is mostly noise.

**Procedure**
1. Scale features using the training data only.
2. Fit PCA, then plot the explained variance per component and cumulatively.
3. Choose how many components by one of these, stating which you used:
   - a cumulative variance target (80–95%, depending on purpose);
   - the elbow in the scree plot;
   - the downstream cross-validated score. This is the best choice when a model consumes the output.
4. Read the loadings. Name a component only after checking which original columns weigh most and in which direction.
5. For denoising, reconstruct from the kept components and inspect the reconstruction error. A large error on a record can flag an anomaly.

**Not for**
- Curved, non-linear structure. Try kernel PCA or UMAP.
- Categorical data.
- Cases where stakeholders need original columns. Select features instead.
- Separating known classes. Use Fisher / LDA.
