# Test plan template

The worked example is a delivery-slot scheduler that assigns orders to vans and time slots. Every expected result is computed by hand or by brute force, never by the model under test.

| Test ID | Requirement | Tier | What it checks | Input | Expected result | Purpose |
|---|---|---|---|---|---|---|
| T-001 | R1 van capacity | Toy | Capacity is enforced | 1 van (capacity 10), 3 orders of size 4 | Two orders on the van, one reported unassigned | Single rule |
| T-002 | R1 van capacity | Toy | Exact fit is allowed | 1 van (capacity 10), orders of size 6 and 4 | Both orders assigned | Boundary |
| T-003 | R2 slot window | Toy | Back-to-back slots are allowed | Slot 9–10 ends exactly as slot 10–11 starts | Both slots used by the same van | Boundary |
| T-004 | R1 + R3 | Medium | Priority beats capacity | Priority order arrives after the van is full | A standard order is bumped; the bump is reported | Conflicting rules |
| T-005 | All | Medium | Last week's plan is feasible | Last Tuesday's manual plan, fixed as input | Feasible, with cost reported | Nothing valid excluded |
| T-006 | All | Toy | Objective is correct | 4 orders, 2 vans | Cost equals the brute-force optimum | Objective sanity |
| T-007 | All | Toy | Infeasible input fails loudly | Order larger than any van | Clear error naming the order | Infeasible input |
| T-008 | All | Large | Performance | 2,000 orders, 60 vans | Under 5 minutes, gap under 2% | Performance |
| T-009 | All | Medium | Determinism | Same input run twice | Identical plan | Determinism |

## Shadow-run log

| Cycle | Model cost | Manual cost | Service level (model / manual) | Plans planners rejected | New test IDs |
|---|---|---|---|---|---|
