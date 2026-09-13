# Model specification template

Write it the way software requirements are written, not the way an academic paper is. Explain each constraint on its own line. Never write "obviously" or "one can easily derive". Write maths in plain text, such as `Sum over j of x[i,j] <= C[j] * y[j]`, so anyone can edit it. Use the same variable names the code will use.

## 1. Business problem
- **Decision:** what gets decided, and how often.
- **Owner:** who acts on it, and how success is measured.
- **Why now:** the pain today or the gain available.
- **In scope / out of scope.**

## 2. Entities
| Set | Meaning | Index |
|---|---|---|
| `SITES` | candidate depot locations | `j` |

## 3. Inputs
| Name in code | Meaning | Unit | Source | Estimate? |
|---|---|---|---|---|
| `demand[i]` | daily orders at zone i | orders/day | last 90 days, median | yes |

## 4. Decision variables
| Name in code | Meaning | Type | Bounds |
|---|---|---|---|
| `open[j]` | 1 if site j opens | binary | 0–1 |
| `ship[i,j]` | orders from site j to zone i | continuous | 0 to `demand[i]` |

## 5. Requirements
| ID | Entity | Rule in words | Hard / soft | Priority | Penalty if soft | Notes |
|---|---|---|---|---|---|---|
| R1 | Zone | Every zone's demand is served or recorded as unmet | Hard | High | — | Unmet demand is a variable, not a deletion |
| R2 | Site | A site ships only if it is open | Hard | High | — | Use the site's capacity as the bound |
| R3 | Site | Prefer utilisation under 85% | Soft | Medium | cost per order above 85% | Protects peak days |

## 6. Constraints, one per requirement
**R2: A site ships only if it is open.**
`Sum over i of ship[i,j] <= capacity[j] * open[j]`, for every site j.
Why: if `open[j] = 0`, nothing ships from site j. If it is open, shipments are capped by capacity.

## 7. Objective
State every term with its unit, and show that the units agree:
`Minimise Sum over j of fixed_cost[j] * open[j] (Rs/day) + Sum over i,j of cost_per_order[i,j] * ship[i,j] (Rs/day) + Sum over i of penalty * unmet[i] (Rs/day)`

## 8. Reading the solution
- Which constraints are binding?
- What is each binding limit worth per unit, and over what range does that value hold?
- Which two or three inputs change the decision if they are wrong?
- What does the decision owner see, and what can they override?
