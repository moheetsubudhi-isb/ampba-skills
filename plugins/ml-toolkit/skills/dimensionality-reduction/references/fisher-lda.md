# Fisher discriminant analysis (LDA)

**Use when** class labels exist and the goal is a low-dimensional view, or features, that separate those classes.

**Idea**
A good direction pushes class means far apart while keeping each class tight. Fisher's criterion is the ratio of between-class scatter to within-class scatter. PCA maximises total variance instead, which can smear classes together.

**Single-feature ranking (Fisher score)**
For two classes: `(mean_A - mean_B)^2 / (var_A + var_B)`. Far means are good. Small within-class spread is good. Use it to rank features quickly.

**Procedure**
1. Scale features and split the data first.
2. Fit `LinearDiscriminantAnalysis` on training data only. The projection has at most `classes - 1` dimensions, so two classes give one dimension.
3. Compare cross-validated downstream accuracy for the LDA projection against PCA with the same number of dimensions. `scripts/projection_check.py --target` does this.
4. LDA can also serve directly as a classifier.

**Assumptions and limits**
- Classes should be roughly Gaussian with similar covariance. Strongly unequal spreads call for quadratic discriminant analysis, or a non-linear model.
- With more features than rows per class, use the shrinkage option (`solver="lsqr", shrinkage="auto"`).
- It sees labels, so fitting it outside cross-validation leaks label information.
