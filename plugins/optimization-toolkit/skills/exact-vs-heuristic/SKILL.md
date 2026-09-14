---
name: exact-vs-heuristic
description: >-
  Choose between an exact solver and a heuristic for a hard planning problem,
  and set honest expectations on speed, plan quality and explainability. Use
  when a routing, delivery, scheduling, rostering, packing, knapsack,
  assignment or network model runs too long or never finishes; when someone
  asks for the optimal plan for hundreds or thousands of stops, jobs or items;
  mentions the travelling salesman or vehicle routing problem, greedy
  algorithms, local or neighbourhood search, genetic algorithms, simulated
  annealing, tabu search, OR-Tools routing, a MIP gap, rolling horizon or
  decomposition; or when planners need a good plan in minutes rather than a
  perfect plan tomorrow.
---

# Exact solver or heuristic

Act as the engineer and the advisor. A good plan by 6 a.m. beats a perfect plan at noon. The decision owner needs to hear three things: how long it takes, how far from the best possible plan it may be, and how much control planners keep.

## Get the context that changes the answer

If a model, solver log or dataset is available, read it first: the problem size, the current run time, the best bound and the MIP gap reached so far.

Then ask only what the request and that material cannot answer, and only when the answer would change the method or the promised run time. Ask at most three questions. Give each one a one-line reason and a default, such as "If you're not sure, I'll assume the plan is needed daily, overnight." If the request is urgent or exploratory, deliver a first cut on stated assumptions and list the questions that would sharpen it.

The questions that usually matter here:

1. **When is the plan needed, and how often?** Real-time, nightly, weekly or once a quarter. The time budget shapes the whole design.
2. **How big is the problem, and which rules apply?** Count the stops, jobs or items, the vehicles or machines, and the periods. List the side rules: time windows, capacities, mixed pickups and drops, shift limits.
3. **Who uses the plan, and what is 1% better worth?** Planners who must understand and override the plan rule out black-box methods. The value of 1% decides how much engineering effort is justified.

If nobody answers, proceed on these defaults and state them: assume the plan is needed once a day within an overnight window, that planners must be able to override individual decisions, and report any heuristic result as a gap against the best known bound rather than as an optimum.

## Procedure

1. **Recognise the problem class and show the scale.** Sequencing and selection problems — the travelling salesman, vehicle routing, job-shop scheduling, knapsack, bin packing, set covering — are NP-hard. The time an exact method needs can explode as size grows. There are 15! ≈ 1.3 trillion orders to visit 15 stops, and 25! ≈ 1.6 × 10^25 orders for 25 stops.
2. **Try the exact solver first**, on a realistic instance with a time limit. Record the best plan found and the solver's bound; the gap between them is the MIP gap. Solvers often reach a provably near-optimal plan well within the limit. If the gap is inside the business's tolerance within the time budget, stay exact.
3. **Otherwise, climb the heuristic ladder.**
   1. **Construct a greedy plan** as a fast baseline. Choose the greedy rule with care. Value per unit of the scarce resource beats a single attribute such as "most valuable first". For routes, visit the nearest unvisited stop next.
   2. **Improve it with neighbourhood search.** Try small moves: relocate a stop to another route, swap stops between routes, or reverse a segment within a route (2-opt). Accept only moves that keep the plan feasible on capacity and time windows.
   3. **Escape local optima.** Restart from several random starting plans. Accept occasional worse moves (simulated annealing, tabu search). Or run a population method: a genetic algorithm that crosses over, mutates and culls plans.
   4. **Use a library** for standard problem classes before writing your own. OR-Tools, for example, covers routing, scheduling, packing and assignment.
4. **Go hybrid when the scale beats both approaches.**
   - **Decompose.** Split the problem by region, depot or period. Solve each piece exactly, then stitch the pieces together heuristically.
   - **Enumerate, evaluate, optimise.** Generate plausible partial routes from business sense. Rank them and prune the weakest. Run the MIP on the top slice. Repeat with the next slice.
   - **Rolling horizon.** Solve a window, freeze its first part, and roll forward with an overlap. For example: solve two weeks, freeze one and a half, repeat. More overlap improves quality but means more solves.
   - **Pipeline.** A greedy start, then MIP improvement, then a local-search polish.
5. **Measure; never assume.**
   - Report every heuristic plan against a bound (an LP relaxation or the solver's bound), or against the proven optimum on small instances. Say "within 3% of the best possible", never just "optimised".
   - Benchmark on several instances, not the one you tuned on.
   - Profile before buying hardware. Parallel runs rarely scale linearly. Seed the randomness so results can be reproduced.
6. **Validate the heuristic on small cases** where the exact answer is known. `scripts/knapsack_check.py` shows how greedy rules compare with the exact optimum, and how to report the gap.

## Deliverable

**Part A: Decision brief**

- The recommended approach, and why it fits the time budget.
- Expected run time, and expected quality as a gap on test instances.
- What planners can control or override.
- The fallback if a run fails, such as reusing the last good plan.

**Part B: Technical appendix**

- Problem class and size, the method stack, and stopping rules.
- A benchmark table with columns: instance · best bound or optimum · heuristic value · gap · run time.

## Traps

- Calling a heuristic plan "optimal".
- Tuning on one instance and reporting results from the same instance.
- A rolling horizon with no overlap, so decisions at the end of one window starve the next.
- Optimising distance while ignoring what dominates on the ground: one-way streets, turn restrictions, parking, loading time.
- A black-box plan planners cannot override. They stop using it.
