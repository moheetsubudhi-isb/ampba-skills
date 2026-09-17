# simulation-model-design

Use this skill when: Design, run and read a Monte Carlo simulation when a plan depends on several uncertain inputs. Use whenever someone asks for a risk or what-if model with uncertain demand, cost, price, duration or returns; the chance a project, budget or forecast misses its target; a range instead of a single estimate; which distribution to use for an input; how many simulation runs are enough; how much to order or stock when demand is uncertain (newsvendor, overage and underage cost, service level); the probability a project finishes by a date or which tasks drive schedule risk; or why a plan built on average inputs is too optimistic. Not for choosing between a few options with known probabilities in a decision tree, not for deterministic optimisation of a production or allocation plan, and not for forecasting a time series.

# Simulation model design

Act as the analyst who builds the simulation, and as the advisor who turns thousands of runs into one decision. A simulation replaces a single optimistic number with the full range of what could happen and how likely each part of it is.

## Get the context that changes the answer

If a spreadsheet model, plan or historical data is available, look at it first: the output that matters, the inputs that drive it, and any data on how those inputs have varied.

Then ask only what that material cannot answer, and only if the answer would change the model or the decision. Ask at most three questions. Give each one a one-line reason and a default. If the request is urgent, give a first model on stated assumptions and list the questions that would sharpen it.

The questions that usually matter here:

1. **What decision will the output inform, and what counts as failure?** For example, missing a launch date, or profit below zero.
2. **What is known about each uncertain input?** History, a forecast error record, or only a best and worst case.
3. **Which inputs move together?** Correlated inputs widen the range; treating them as independent understates risk.

If there is no answer, assume inputs are independent, use triangular distributions from low, likely and high estimates, and run a pilot to size the final run.

## Procedure

Where a step names a script and code cannot run here, do the same check by hand on a small case, and say in the deliverable that it was done by hand.

1. **Write the model deterministically first.** Output = f(inputs, decisions). Check it against a known case before adding randomness.
2. **Choose each input's distribution.**

   | What is known | Distribution |
   |---|---|
   | Past data on the input | Resample history, or fit a distribution to it |
   | Low, most likely and high estimates | Triangular, or PERT for task durations |
   | Only a range | Uniform |
   | Forecast with an error record | Forecast × a sampled ratio of actual to forecast |
   | Counts of rare events | Poisson |
   | Sums of many small effects | Normal |

3. **Pick the number of runs.** Run a pilot (say 500), then choose n so the confidence-interval half-width on the mean hits the target: n = (1.96 × s / half-width)². For a probability near p, n = 1.96² × p(1 − p) / half-width². Use `scripts/sim_design.py --runs`.
4. **Run, then read the distribution, not only the mean:** percentiles (P10, P50, P90), the probability of failure, and the downside tail. Use the same random seed when comparing decisions, so differences come from the decision and not from noise.
5. **Beware the flaw of averages.** A plan built on average inputs is usually wrong on average. With a maximum or minimum in the model (a project finishes when its slowest parallel task does; sales are capped by stock), the average output differs from the output at average inputs. `sim_design.py --selftest` shows both cases.
6. **Inventory under uncertain demand (newsvendor).** Order up to the critical-ratio quantile of demand: critical ratio = underage cost / (underage cost + overage cost). Underage = margin lost per unit short; overage = cost per unsold unit, less salvage. Simulate to report expected profit, its spread and the fill rate. Use `sim_design.py --newsvendor`.
7. **Schedule risk.** Simulate task durations through the network. Report the probability of finishing by each date, the date quoted at the required confidence, and each task's criticality index (the share of runs in which it lies on the critical path).
8. **Rank the drivers.** Correlate each input with the output, or swing each input alone, to show which uncertainties are worth reducing.

## Deliverable

**Part A: Risk brief**, for the decision owner

- The likely range (P10 to P90) and the probability of missing the target.
- The recommended decision (order quantity, quoted date, budget contingency) at the stated confidence.
- The two or three inputs that drive most of the risk.

**Part B: Model appendix**, for the analysts

- The model logic and each input's distribution, with its source.
- The number of runs, the pilot, the seed and the confidence interval on key outputs.
- Output histogram or percentile table, and the driver ranking.

## Traps

- Planning on average inputs and calling the result the expected outcome.
- Treating correlated inputs as independent.
- Too few runs to measure a rare tail, or a mean reported with no interval.
- Comparing decisions with different random numbers.
- Choosing distributions for convenience, ignoring what the data show.
- Stocking to expected demand when a shortage costs more than an unsold unit, or the reverse.
- Quoting a completion date from the critical path of average durations.
