---
name: shortage-allocation-fairness
description: >-
  Decide who gets what when there is not enough to go round, and explain the
  trade-off between efficiency and fairness to the people affected. Use when a
  planning or optimisation model is infeasible because demand exceeds supply;
  when a plan starves one customer, store, region or team while another gets
  everything; when allocating scarce stock, budget, capacity, staff, delivery
  slots, appointments or medicines; when someone asks for a fair, equal,
  proportional or priority-based allocation, min-max, a penalty for unmet
  demand or slack variables; or when stakeholders reject an optimiser's plan
  as unfair even though it has the lowest total cost. Not for testing,
  validating or signing off an allocation model that already works.
---

# Shortage allocation and fairness

Act as the analyst and the advisor. Making the model feasible is technical. **Choosing what "fair" means is a value judgement that belongs to the decision owner.** Your job is to set out the options and what each one costs, recommend one, and make the choice explicit. Never decide it quietly inside an objective function.

## Get the context that changes the answer

If demand, supply or an existing allocation is available, look at it first: total demand against total supply, how uneven the claimants are in size, and who the current plan starves.

Then ask only what the request and that material cannot answer, and only when the answer would change who receives what. Ask at most three questions. Give each one a one-line reason and a default, such as "If you're not sure, I'll assume claimants differ in size, so we compare the percentage of need met." If the request is urgent or exploratory, deliver a first cut on stated assumptions and list the questions that would sharpen it.

The questions that usually matter here:

1. **Who are the claimants, and are their needs comparable?** A 5-unit clinic and a 500-unit hospital cannot share shortfall in raw units. Compare them on the percentage of need met.
2. **What does fair mean here?** Offer these options:
   - equal shortfall in units,
   - equal percentage of need met,
   - protect the worst-off claimant first,
   - priority tiers, such as contracted, critical or strategic,
   - shares in proportion to history.
3. **How much total output may be given up to buy fairness?** For example, "no more than 2% fewer units shipped."

If nobody answers, proceed on these defaults and make them visible: compare claimants on the percentage of need met, protect the worst-off first and then maximise the total served (the two-stage rule), and present the efficient plan alongside it with the price of fairness attached.

## Procedure

1. **Make the model feasible without hiding the shortage.** Give every claimant an unmet-demand variable: `served[i] + unmet[i] == demand[i]`. Never delete the demand constraint.
   - If demand is written as `served[i] <= demand[i]` with no penalty or revenue, a cost-minimising model will serve no one.
2. **Solve for efficiency first**: minimise total unmet demand, or maximise served value. Check for ties. Many allocations often share the best total, and the solver returns one of them arbitrarily. A plan that looks unfair may simply be a tie-break accident.
3. **Lay out the fairness options.**
   - **Protect the worst-off (min-max).** Minimise `W` subject to `W >= unmet[i]`, or `W >= unmet[i] / demand[i]` when needs differ. This is linear and fast. Its weakness is that it only looks at the worst claimant. Many plans tie, and some of them leave supply unused.
   - **Spread the pain (squared penalty).** Minimise the sum of `unmet[i]^2`, or `(unmet[i] / demand[i])^2`. Every claimant counts. It is nonlinear, so solves are slower. Keep it linear with a piecewise approximation: split `unmet` into equal-width segments whose cost slopes increase. For `s^2` with segment width `w`, segment `k` (counting from 0) has slope `(2k + 1) * w`.
   - **Two-stage (usually the right default).** Stage 1: minimise the worst percentage of need unmet. Stage 2: fix that worst case, and minimise total unmet demand. This protects the worst-off and wastes no supply.
   - **Priority weights.** Minimise `weight[i] * unmet[i]` when tiers are agreed policy.
4. **Show the options side by side** on a small version of the problem with `scripts/compare_fairness.py`. Pass `--value` when a unit served is worth more for some claimants than others. The script lists the plan each rule chooses, how many plans tie, each plan's worst-off claimant, and its price of fairness.
5. **Put a price on fairness.** Compare total served, or total profit, between the fairest plan and the most efficient plan. That gap is the price. Decision owners accept a price they can see far more readily than a rule someone else chose for them.

## Deliverable

**Part A: Decision brief**

- **The shortage in one line:** "Needed 30, have 20."
- **Two to four candidate plans** in a table: who gets what, the percentage of need met for each claimant, total served, and the worst-off claimant's percentage.
- **The price of fairness** for each plan, compared with the most efficient one.
- **Recommendation**, and the definition of fairness it commits the business to.
- **A sentence the affected parties will understand**, such as "Every store receives at least 60% of its order this week."

**Part B: Technical appendix.** The formulation for each option, the tie-breaking notes, and any piecewise segments used.

## Traps

- Deleting constraints until the model solves. The shortage vanishes from the report but not from reality.
- Presenting a tie-break accident as a deliberate allocation.
- Comparing raw units across very different sizes of need.
- Min-max on its own, which can leave supply on the shelf. Add the second stage.
- Choosing the definition of fairness on the owner's behalf. Recommend one, but make the choice visible.
