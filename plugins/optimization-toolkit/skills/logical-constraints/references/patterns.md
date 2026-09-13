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
