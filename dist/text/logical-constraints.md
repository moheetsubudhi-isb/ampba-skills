# logical-constraints

Use this skill when: Write yes/no business rules as correct linear constraints in a mixed-integer model, then prove them right by enumeration. Use whenever a model needs if-then or only-if logic, either/or choices, at most k or exactly one of a set, AND/OR conditions, a fixed cost that applies only when something is used, a minimum batch size, min, max or absolute-value terms, deciding which shift or time slot a value falls in, big-M, indicator or binary variables, or linearising a product of variables. Also use when a MIP returns plans that break a rule everyone believed was modelled, or runs slowly because of a huge big-M.

# Logical constraints

Act as the modeller and the advisor. Before turning a rule into maths, make sure it is a real business rule. Decide whether it is absolute or a preference. Explain what it costs in solve time and flexibility.

## Get the context that changes the answer

If a model, code or constraint list is available, read it first: variable names and types, existing bounds, the objective, and any big-M values already in use.

Then ask only what the request and that material cannot answer, and only when the answer would change the constraint you write. Ask at most three questions. Give each one a one-line reason and a default, such as "If you're not sure, I'll assume the rule is absolute, not a preference." If the request is urgent or exploratory, deliver a first cut on stated assumptions and list the questions that would sharpen it.

The questions that usually matter here:

1. **The rule in the owner's own words.** Is it absolute ("never"), or a preference ("try not to")? A preference becomes a penalty, not a constraint.
2. **Variable types and real bounds.** The bounds set the big-M values. "Capacity is 1,200 orders a day" is a bound; 10^9 is not.
3. **Objective direction for the variable being defined.** Is it maximised, minimised, or absent from the objective? Some formulations only work in one direction. `c <= a, c <= b` gives a correct AND only when the objective pushes `c` up.

If nobody answers, proceed on these defaults and say so: treat the rule as hard, take bounds from the data or the model, and write the version that is correct in both objective directions. The direction-independent form costs one extra constraint and cannot silently break later.

## Procedure

Where a step names a script and code cannot run here, do the same check by hand on a small case, and say in the deliverable that it was done by hand.

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

---

## Reference: references/patterns.md

# Logic-to-linear patterns

Lower-case letters are binary (0/1) unless stated. `U` is a real upper bound, `L` a real lower bound, `M` the smallest valid big-M. Check any pattern with `scripts/truth_table.py`.

## Binary rules
| Rule | Constraints |
|---|---|
| If A then B | `a <= b` |
| A and B not both | `a + b <= 1` |
| Exactly one of A, B | `a + b == 1` |
| At least one of A, B | `a + b >= 1` |
| At most k of a set | `sum(x) <= k` |
| Exactly k of a set | `sum(x) == k` |
| c = NOT a | `c == 1 - a` |
| c = a AND b, any objective | `c <= a`, `c <= b`, `c >= a + b - 1` |
| c = a AND b, only if c is maximised | `c <= a`, `c <= b` |
| c = a OR b (c true if and only if a or b) | `c >= a`, `c >= b`, `c <= a + b` |
| c = a × b (product of binaries) | same as AND |

## Binary switching continuous
| Rule | Constraints |
|---|---|
| Use x only if y is on | `x <= U * y` (use the real capacity for U) |
| Minimum batch when produced | `x >= L * y`, `x <= U * y` |
| Fixed cost when used | add `F * y` to the cost, with `x <= U * y` |
| w = b × x, with 0 ≤ x ≤ U | `w <= U * b`, `w <= x`, `w >= x - U * (1 - b)`, `w >= 0` |
| At least one of two constraints holds: g1(x) ≤ 0 or g2(x) ≤ 0 | `g1(x) <= M * b`, `g2(x) <= M * (1 - b)` |

## Continuous relationships
| Rule | Constraints |
|---|---|
| At least 5 units of x2 per unit of x1 | `5 * x1 <= x2` |
| Shared capacity: a line makes 20 A or 50 B per shift, over 10 shifts | `A / 20 + B / 50 <= 10` |
| z = min(x, y), z maximised | `z <= x`, `z <= y` |
| z = min(x, y), any objective | `z <= x`, `z <= y`, `z >= x - M * (1 - b)`, `z >= y - M * b` |
| z = max(x, y), z minimised | `z >= x`, `z >= y` |
| z = max(x, y), any objective | `z >= x`, `z >= y`, `z <= x + M * (1 - b)`, `z <= y + M * b` |
| Minimise \|x1 - x2\| | `z >= x1 - x2`, `z >= x2 - x1`, minimise z |
| Maximise \|x1 - x2\| | `z <= x1 - x2 + M * (1 - b)`, `z <= x2 - x1 + M * b`, maximise z |

## Which slot a value falls in
Slots `k` with boundaries `lo[k]` to `hi[k]`, and binary `y[k]`:
`sum(y) == 1`, `t >= sum(lo[k] * y[k])`, `t <= sum(hi[k] * y[k])`.
Example with three 8-hour shifts: `t >= 0*y1 + 8*y2 + 16*y3`, `t <= 8*y1 + 16*y2 + 24*y3`.
A value exactly on a boundary (such as t = 8) fits two slots. State which slot boundaries belong to.
