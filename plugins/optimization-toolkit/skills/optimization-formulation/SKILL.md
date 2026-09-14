---
name: optimization-formulation
description: >-
  Turn a business decision into an optimisation model and a recommendation a
  business owner can act on. Use whenever someone needs to decide how much to
  make, buy, stock, staff or ship; where to open sites or depots; how to split
  a budget, capacity, people or inventory; or asks for the best plan, maximum
  profit or minimum cost given limits, a production mix, facility location,
  capacity planning, prescriptive analytics, linear programming or a MIP. Also
  use when someone asks whether an investment in capacity, overtime, marketing
  or extra supply is worth it, what extra capacity is worth, how to read a
  solver's output, or needs a model requirements document for developers. Not
  for a model that already exists and only runs too slowly, and not for
  deciding who gets cut back when supply cannot cover demand.
---

# Optimisation formulation

Act as a decision scientist who is also the decision owner's advisor. The goal is a better decision, not a model. Sometimes the best advice is that no model is needed.

## Step 0: Check it is an optimisation problem

Analytics answers four different questions: what happened, why it happened, what will happen, and what we should do. Optimisation answers only the last one, and only when three things are true:

- there are real choices to make,
- there is a measurable goal, and
- limits force those choices to compete.

If the actual gap is a missing forecast, unreliable data, or an unclear goal, say so and stop there. If there are only a handful of options, compare them in a table instead of building a model.

## Get the context that changes the answer

If data, a schema or a current plan is available, look at it first: the entities involved, their counts, the ranges of costs and capacities, and which limits are already close to binding.

Then ask only what the request and that material cannot answer, and only when the answer would change the model or the recommendation. Ask at most three questions. Give each one a one-line reason and a default, such as "If you're not sure, I'll assume we are optimising total cost for the operations owner." If the request is urgent or exploratory, deliver a first cut on stated assumptions and list the questions that would sharpen it.

The questions that usually matter here:

1. **Whose decision is it, and what does winning mean to them?** Different owners want different objectives for the same problem. Placing EV chargers: drivers want coverage of people, a regulator wants coverage of area, the operator wants revenue, the utility wants steady grid load. When several owners are involved, name the conflict. Never pick one objective silently.
2. **What exactly does the target mean?** "Within 30 minutes of 90% of customers" could mean 90% of customers or 90% of order volume, nationally or in every region. Each reading produces a different network.
3. **What is fixed, what can change, over what period, and how often is this decided?** A one-off strategic decision needs a different model from a plan rebuilt every morning.

If nobody answers, proceed on these defaults and print them at the top of the output: optimise cost for the team that owns the operation, read a coverage target as covering demand volume rather than customer count, and model one planning period.

## Procedure

1. **Entities.** List the sets involved: products, sites, customers, time periods.
2. **Inputs.** Give each input a unit and a source. Mark which ones are estimates.
3. **Decision variables.** Type each one as continuous, integer or binary, and say why. For example, bags of loose material are continuous; trucks are integers; open or closed is binary.
4. **Constraints as requirements.** Give each rule an ID, a plain-language statement, a priority, and a type: hard or soft. A soft rule gets a slack variable with a penalty. Never drop a rule silently.
5. **Objective.** Check the units before adding terms together. Never add kilometres to rupees. Convert everything to one unit, or state the weights explicitly.
   - If demand is written as "serve up to demand", a cost-minimising model will serve nobody. Give served demand a revenue, or give unmet demand a penalty.
6. **Classify the model.** Linear constraints and a linear objective make an LP. Integer or binary variables make a MIP. Volume discounts or squared penalties make it nonlinear; use a piecewise-linear approximation to keep it linear. If the problem is routing, sequencing or scheduling at scale, apply the exact-versus-heuristic reasoning before promising run times.
7. **Solve a tiny instance first.** Use data small enough to check by hand. Any solver works: OR-Tools, HiGHS or PuLP, Excel Solver. Scale up only after the tiny case gives the answer you expect.
8. **Read the solution as an advisor.**
   - **Binding constraints** are the limits actually holding the result back. Only loosening one of these can improve the outcome.
   - **Money spent loosening a non-binding limit is wasted.** Example: marketing proposes a campaign to raise demand for the premium product. Labour hours and a shared component are binding; demand is not. More demand adds zero profit, and the campaign cost becomes a pure loss.
   - **What extra capacity is worth.** Re-solve with the limit raised by the proposed amount. The gain in the objective is the most worth paying for that increment. Report the value per unit and in total. State that it only holds while the same constraints stay binding.
   - **Several levers at once.** When levers interact (overtime and a campaign together, say), do not compare separate runs. Build one model with a binary "use this lever" variable and its fixed cost. The solver then picks the best combination.
9. **Stress-test.** Find the two or three inputs that change the decision if they are 10–20% wrong. Re-solve with those inputs changed, and report which decisions move.

## Deliverable

**Part A: Decision brief** — for the decision owner, with no maths.

- The recommendation, in one sentence.
- The expected impact, with number, unit and period, against today's baseline.
- What is holding the result back, and what loosening each limit is worth.
- What was deliberately left out of the model.
- The single assumption the answer depends on most, and what would change it.

**Part B: Model specification** — for the people who build it. Follow `references/model-spec.md`.

## Traps

- Optimising the wrong stakeholder's objective, because nobody asked whose it was.
- Adding terms with different units.
- "Serve up to demand" with no revenue or penalty, so the model serves no one.
- Deleting constraints to make an infeasible model solve. Add slack instead, and report which limit broke.
- Handing over the optimum without its binding constraints and sensitivity. A number without a reason will not be trusted.
- Treating the model's output as the decision. The model is the brain; planners also need a view to act on it, such as plan comparisons and changes since yesterday.
