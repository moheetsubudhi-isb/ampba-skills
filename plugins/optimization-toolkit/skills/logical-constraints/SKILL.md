---
name: logical-constraints
description: >-
  Write yes/no business rules as correct linear constraints in a mixed-integer
  model, then prove them right by enumeration. Use whenever a model needs
  if-then or only-if logic, either/or choices, at most k or exactly one of a
  set, AND/OR conditions, a fixed cost that applies only when something is
  used, a minimum batch size, min, max or absolute-value terms, deciding which
  shift or time slot a value falls in, big-M, indicator or binary variables,
  or linearising a product of variables. Also use when a MIP returns plans
  that break a rule everyone believed was modelled, or runs slowly because of
  a huge big-M.
---

# Logical constraints

Act as the modeller and the advisor. Before turning a rule into maths, make sure it is a real business rule. Decide whether it is absolute or a preference. Explain what it costs in solve time and flexibility.

## Intake

Ask only what the request leaves unclear.

1. **The rule in the owner's own words.** Is it absolute ("never"), or a preference ("try not to")? A preference becomes a penalty, not a constraint.
2. **Variable types and real bounds.** The bounds set the big-M values. "Capacity is 1,200 orders a day" is a bound; 10^9 is not.
3. **Objective direction for the variable being defined.** Is it maximised, minimised, or absent from the objective? Some formulations only work in one direction. `c <= a, c <= b` gives a correct AND only when the objective pushes `c` up.

## Procedure

1. **Restate the rule as logic and confirm it in words.** For example: "Site closed means it serves zero orders. A site that serves one order still pays full rent. Correct?"
2. **Pick the pattern** from `references/patterns.md`.
3. **Write the linear form.**
   - Never multiply two decision variables.
   - Use the smallest big-M the real bounds allow. Prefer a bound from the business: `orders[j] <= capacity[j] * open[j]` beats `orders[j] <= M * open[j]`. It is tighter, it solves faster, and it enforces capacity at the same time.
4. **Prove it.**
   - When all variables are binary or small integers, run `scripts/truth_table.py`. It tries every situation and compares what the constraints allow with what the rule requires. If the rule only holds under one objective direction, pass `--sense` and `--target`.
   - For continuous variables, test by hand at the boundaries: zero, exactly at the bound, and just over it.
   - With no Python available, write out the table for two or three variables by hand.
5. **Hand back the result** in the format below.

Example check, run from this skill's folder:

```
python3 scripts/truth_table.py --given a b --decide c \
  --constraint "c <= a" --constraint "c <= b" --constraint "c >= a + b - 1" \
  --rule "c == (a and b)"
```

## Deliverable

For each rule:

- **Rule:** in plain words.
- **Logic:** for example, `open → capacity used ≤ capacity`.
- **Constraints:** ready to paste into the model.
- **Proof:** PASS from `truth_table.py`, or the boundary cases checked by hand.
- **M:** the value used and where it comes from.
- **Direction dependence:** whether the constraints are only correct when maximising or when minimising.
- **Business note:** a side effect the owner should confirm, such as "opening a site for one order triggers the full fixed cost".

## Traps

- An AND or MIN written for maximisation, then reused in a minimising model.
- A big-M of 10^9. It weakens the relaxation, slows the solver and causes numerical trouble.
- A "must" that is really a "prefer". The model goes infeasible when the business would have bent the rule.
- Rules added one by one with nobody checking them together. Run the proof on the combined constraints.
