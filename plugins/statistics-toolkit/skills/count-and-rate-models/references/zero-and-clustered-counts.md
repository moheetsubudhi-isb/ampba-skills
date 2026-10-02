# Too many zeros, and repeated units

## Too many zeros

A Poisson or negative binomial model expects a certain share of zeros given its average. If the data have clearly more, ask why before reaching for a model.

| Cause of the extra zeros | What to do |
|---|---|
| An important predictor is missing (the product was not stocked, the store was closed) | Add the predictor or filter those rows; the zeros may disappear |
| Two different processes: "did anything happen at all?" then "how many?" | Hurdle model: a yes/no model for any count, then a count model for the positive values |
| Some units can never produce a count (structural zeros) mixed with units that can | Zero-inflated model: a mix of an always-zero group and a count group |
| Counts recorded only when positive | Fix the data: missing is not zero |

**Hurdle versus zero-inflated.** Choose a hurdle model when every zero means "did not start" and every positive count comes from a separate process. Choose zero-inflated when some zeros are structural and others are ordinary zeros from a count process. Use either only when the two-process story is believable, not merely because the fit improves.

**Reading the two parts.** In a two-part model the first part's coefficients change the chance of any count (report as odds), and the second part's change how many (report as rate ratios). The expected count is the product of the chance of a positive and the expected size given positive.

## Repeated units

Rows from the same product, store or customer are more alike than rows from different ones, so standard errors from an ordinary count model are too small.

- **Cluster-robust standard errors** keep the coefficients and widen the errors, using the unit as the cluster. Good when the aim is to report effects.
- **Multilevel (mixed-effects) count model** gives each unit its own baseline rate. Good when the aim is to predict for known units, or when units differ a lot.
- **Validation.** Hold out whole units (to test prediction for new units) or whole later periods (to test forecasting), not random rows, or the score will look better than reality.

## Other signs Poisson is not enough

| Sign | Response |
|---|---|
| Counts more regular than Poisson (variance below the mean) | A model with a dispersion parameter that can fall below 1, or a specialised count family |
| A clear trend or season | Add time terms; validate on later periods |
| An upper limit to the count (at most n trials) | A binomial model for successes out of trials |
| Very large counts | A model on the log scale with a constant-variance error may be as good |
