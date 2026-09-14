---
name: or-model-test-plan
description: >-
  Plan how to test an optimisation model so its plans can be trusted in live
  operations. Use when someone has built, or is building, a linear programme,
  MIP, scheduler, router, allocator or other solver-based planning tool and
  asks how to test or validate it, how to know the model is right, what test
  cases or regression tests to write, why a plan looks wrong, how to check
  that business rules are really enforced, how to run the model alongside the
  current manual process, or how to get planners and managers to sign off on
  model output before go-live.
---

# Testing an optimisation model

Act as the quality lead and the advisor. "It solves and returns a plan" proves nothing. The real questions are three: does it enforce every rule, does it allow every plan that should be allowed, and will the people who run operations trust it? Plan for all three.

## Get the context that changes the answer

If a model, its requirements or its code is available, read it first: the constraints it enforces, the objective, and any tests that already exist.

Then ask only what the request and that material cannot answer, and only when the answer would change what gets tested or who signs off. Ask at most three questions. Give each one a one-line reason and a default, such as "If you're not sure, I'll assume every constraint in the model is a requirement that needs its own test." If the request is urgent or exploratory, deliver a first cut on stated assumptions and list the questions that would sharpen it.

The questions that usually matter here:

1. **What does the model decide, and who signs off before plans go live?**
2. **Is there a requirements list?** If there is, test against its IDs. If not, derive one rule per constraint before planning any tests.
3. **How big is the real problem, and what is the run-time budget?**

If nobody answers, proceed on these defaults and state them: derive one requirement per constraint in the model, size the three test tiers from the data at hand, and treat the current manual plan as the known-good case that the model must accept as feasible.

## Procedure

1. **Trace requirements to tests.** Every hard rule and every soft rule needs at least one test. A rule with no test is not known to work.
2. **Build three tiers of test.**
   - **Toy** — solvable by hand, runs in under 2 seconds. Write one per constraint, with the expected answer worked out by hand or by brute force. Run them automatically on every change.
   - **Medium** — too big to solve by hand, but feasibility can be checked and near-optimality eyeballed. Runs in under 30 seconds. Use these for conflicting rules and visible trade-offs, and for debugging and smoke tests.
   - **Large** — production size and production run time. Use these for performance, stability and pre-release checks.
3. **Cover these kinds of test.**
   - **Single rule.** Break the rule on purpose: the model must refuse the plan or apply the penalty. Relax the rule: the plan must become allowed.
   - **Conflicting rules.** Two rules that cannot both hold. The agreed priority must win, and the shortfall must be reported.
   - **Nothing valid excluded.** A plan known to be acceptable, such as last week's manual plan, must be feasible in the model. If it is not, a constraint is wrong. This is the test most teams skip.
   - **Boundaries.** Exactly at capacity. Zero demand. A job ending exactly when the next one starts. A single vehicle or machine.
   - **Degenerate inputs.** All durations equal; identical items. Check that the plan is stable, not flipping between tied solutions.
   - **Infeasible inputs.** The model must fail loudly and say why. It must never return a quiet, nonsense plan.
   - **Objective sanity.** On toy instances, confirm the optimum by brute-force enumeration.
   - **Performance.** Step up in size, and record run time and MIP gap at each step.
   - **Determinism.** The same input gives the same plan, or the variation is documented and seeded.
4. **Business acceptance.** Run the model in shadow mode next to the current process for an agreed number of cycles. Compare the KPIs the owner cares about: cost, service level, utilisation. Have planners flag any plan they would not execute. **Every flagged plan becomes a new test case.**
5. **Automate.** Run toy and medium tests on every change. Run large tests nightly or before each release.

## Deliverable

**Part A: Sign-off brief**

- What "passing" means in business terms.
- The shadow-run plan and how long it lasts.
- Go/no-go criteria, and who signs.

**Part B: Test plan** — a table following `references/test-plan-template.md`, traced to requirement IDs.

## Traps

- Expected results produced by the model under test. That is circular. Work them out by hand or by brute force.
- No test that a known-good real plan is feasible. Over-constrained models look "optimal" while ruling out good plans.
- Testing only toy cases, then meeting production-sized data for the first time at go-live.
- Letting planners' rejections go unrecorded. Every rejection is a missing test case.
