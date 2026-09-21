# decision-tree-analysis

Use this skill when: Decide between options whose payoff depends on uncertain outcomes, using a decision tree and expected monetary value (EMV). Always use this skill when someone asks whether to launch, invest, expand, bid, settle, build or drill and gives, or can estimate, payoffs and the chances of each outcome, even when the question sounds like a simple yes or no. Also use it to lay out decision and chance nodes and fold the tree back; compare several risky options; test how sensitive the choice is to a probability or payoff, or find the breakeven probability where it flips; or decide whether risk aversion, a utility function or a worst-case view should override expected value. Not for decision tree, random forest or boosting models trained on data, not for pricing a test, survey or pilot before deciding, not for simulating many uncertain inputs, and not for explaining what a decision tree is when no decision is in play.

# Decision tree analysis

Act as the decision analyst who lays out the choice, and as the advisor who says how firm the recommendation is. The tree is a thinking tool: its value is in exposing what the decision really hinges on.

## Get the context that changes the answer

If a proposal, business case or spreadsheet is available, look at it first: the options on the table, the uncertain events, the cash flows, and any probabilities already estimated.

Then ask only what that material cannot answer, and only if the answer would change the tree or the recommendation. Ask at most three questions. Give each one a one-line reason and a default. If the request is urgent, give a first tree on stated assumptions and list the questions that would sharpen it.

The questions that usually matter here:

1. **What are all the options, including doing nothing or waiting?** The best option is often one nobody wrote down.
2. **Where do the probabilities come from?** History, experts or a guess; this sets how much sensitivity analysis is needed.
3. **Could the business survive the worst outcome?** If not, expected value alone is the wrong rule.

If there is no answer, assume "do nothing" is an option, probabilities are expert guesses, and the business is risk-neutral for amounts small against its size.

## Procedure

Where a step names a script and code cannot run here, do the same check by hand on a small case, and say in the deliverable that it was done by hand.

1. **Draw the time order.** Decision nodes (squares) are choices the business controls. Chance nodes (circles) are events it does not. Order them as the business will experience them: what is known at each decision must already have happened to the left of it.
2. **Put money on the leaves.** Each end point gets the total net cash flow along its path: costs incurred plus the final payoff. Discount if outcomes land years apart.
3. **Assign probabilities** at each chance node. They must sum to 1, and they may depend on earlier branches.
4. **Fold back.** From right to left: at a chance node take the probability-weighted average (EMV); at a decision node take the best branch. Run `scripts/decision_tree.py` on a JSON tree; it returns the EMV, the best strategy and the risk profile of that strategy (each possible outcome and its probability).
5. **Test sensitivity.** Vary each uncertain probability and the largest payoffs one at a time across their plausible range. Report the breakeven value where the best decision changes, with `decision_tree.py --sweep`. A decision that never flips across the plausible range is robust, and more analysis will not change it.
6. **Check risk.** EMV assumes the business can absorb a bad outcome. Compare the risk profiles: the chance of a loss and the size of the worst case. When a loss would be ruinous, use a utility function or a certainty equivalent, or pick the option whose worst case is survivable, and say why.
7. **Ask whether to learn more first.** If a test, survey or pilot could reveal the uncertain outcome, value it with the value-of-information skill before deciding.

## Deliverable

**Part A: Decision brief**, for the decision owner

- The recommended option and its expected value, in one sentence.
- What the decision hinges on: the breakeven probability or payoff, set against the current estimate.
- The risk: the chance of losing money and the worst case.

**Part B: Analysis appendix**, for the analysts

- The tree, with probabilities, payoffs and folded-back values.
- The sensitivity table and breakeven points.
- The risk profile of each option, and any utility assumption.

## Traps

- Leaving out "do nothing", "wait" or a staged option.
- Putting a decision after the event it depends on, or before information that will actually be available.
- Counting a cost twice: once on a branch and again in the leaf payoff.
- Presenting EMV as what will happen; it is the average over many repetitions of a decision made once.
- Probabilities that do not sum to 1, or are copied between branches where they should differ.
- Reporting one answer with no sensitivity analysis.
- Using EMV when the worst case would sink the business.
