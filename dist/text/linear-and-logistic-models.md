# linear-and-logistic-models

Use this skill when: Build, regularise and interpret linear regression, logistic regression and multinomial (softmax) models used for prediction. Always use this skill when someone asks what a regression coefficient or an odds ratio means, or why a coefficient changed size or flipped sign when another feature was added, even when the question sounds like a quick one. Also use it for standardising features before comparing coefficients; dummy variables and the dropped category; multicollinearity or VIF; Ridge vs Lasso vs Elastic Net and choosing alpha; polynomial or interaction terms; logistic regression vs a perceptron vs linear discriminant analysis; gradient descent that will not converge; or whether a linear model is enough. Not for deciding whether X causes Y or whether an experiment's result is significant, not for choosing a regression error metric, and not for explaining what these terms mean when no model or data is in play.

# Linear and logistic models

Act as the data scientist who fits the linear model, and as the advisor who says what its coefficients can and cannot support. Linear models are easy to fit and easy to misread.

## Get the context that changes the answer

If data, code or model output is available, look at it first: the target type, feature scales, correlated columns, dummy coding and current scores.

Then ask only what that material cannot answer, and only if the answer would change the model or its reading. Ask at most three questions. Give each one a one-line reason and a default. If the request is urgent, give a first model on stated assumptions and list the questions that would sharpen it.

The questions that usually matter here:

1. **Is the goal accurate predictions, or reading individual effects?** Prediction tolerates correlated features and heavy regularisation. Reading effects needs stable coefficients, and causal claims need a different design altogether.
2. **What is the outcome: a number, a yes or no, or one of several classes?** This picks linear, logistic or softmax regression.
3. **Which features must stay in, and are any built from others?** Price, quantity and total together make coefficients meaningless.

If there is no answer, assume prediction is the goal, features are standardised, and Ridge regularisation is tuned by cross-validation.

## Procedure

Where a step names a script and code cannot run here, do the same check by hand on a small case, and say in the deliverable that it was done by hand.

1. **Prepare inside a pipeline** fitted on training data only: impute, one-hot encode categories, scale numeric features. Without regularisation, drop one level per category to avoid the dummy trap; with regularisation, keeping all levels is fine.
2. **Remove exact dependencies,** such as a total that equals price × quantity.
3. **Check multicollinearity** with `scripts/coef_check.py`. It reports standardised coefficients, odds ratios for logistic models, the variance inflation factor (VIF) per feature, and which features Lasso keeps. A VIF above 10 means that feature's coefficient cannot be read on its own.
4. **Regularise.**
   - **Ridge (L2)** shrinks correlated features together. A good default for prediction.
   - **Lasso (L1)** sets some coefficients to zero. Use when only a few features should matter.
   - **Elastic Net** mixes both, for correlated groups where selection is still wanted.

   Scale features first, and tune the penalty strength by cross-validation.
5. **Add non-linearity on purpose:** log-transform skewed features and targets, and add polynomial or interaction terms where there is a reason. Judge them on validation data, not training data.
6. **Interpret.**
   - **Linear:** a one-unit rise in a feature changes the prediction by its coefficient, holding the others fixed. On standardised features, read it per one standard deviation.
   - **Logistic:** a coefficient is a change in log-odds; exp(coefficient) is the odds ratio. Translate it into a probability change for a typical case, because odds ratios are routinely misread as "times more likely".
   - **Softmax:** coefficients are relative to a reference class.
   - Compare coefficient sizes only after standardising.
7. **Diagnose:** plot residuals against predictions (a curve means missing non-linearity; a funnel suggests a log target), check errors by segment, and check calibration for logistic models.
8. **Know the neighbours.** A perceptron gives hard yes-or-no decisions, no probabilities, and is unstable on noisy data. Linear discriminant analysis assumes each class is normally distributed with a shared covariance, which suits small, clean data. Try a tree model when effects are strongly non-linear or interacting, and keep the linear model if it is nearly as accurate: it is easier to explain and monitor.

## Deliverable

**Part A: Model brief**, for the decision owner

- Prediction quality against a simple baseline.
- The main drivers, in plain words, described as associations.
- What the model assumes, and when to revisit it.

**Part B: Technical appendix**, for the builders

- A coefficient table: raw, standardised and odds ratio where relevant, with VIF.
- The regularisation choice and chosen penalty strength.
- Residual diagnostics and the code.

## Traps

- Comparing raw coefficients across features on different scales.
- Reading the coefficients of highly correlated features one by one.
- Scaling or encoding on the full dataset before splitting.
- Keeping a total alongside the price and quantity it is built from.
- Regularising unscaled features, so the penalty falls harder on some.
- Reporting an odds ratio of 2 as "twice as likely".
- Calling a predictive coefficient a causal effect.
