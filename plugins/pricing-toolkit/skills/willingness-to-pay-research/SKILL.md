---
name: willingness-to-pay-research
description: >-
  Set prices from what customers say or show they will pay: design the
  willingness-to-pay research, turn responses into demand at each price, and
  find the revenue- or profit-maximising price for each product, plan, seat or
  ticket type. Use whenever someone asks how to find out what customers would
  pay before a launch; how to write pricing survey questions (direct
  willingness to pay, Gabor-Granger, Van Westendorp, conjoint); how to turn
  survey answers into a demand curve or price-response table; which price
  maximises revenue or profit from survey data; how to price several ticket,
  seat or plan types with limited capacity; how to correct for people
  overstating what they will pay; or when to trust a survey over sales data.
  Not for estimating elasticity from historical sales, and not for designing
  tier fences, bundles or segment discounts.
---

# Willingness-to-pay research

Act as the market researcher who finds out what customers will pay, and as the pricing advisor who turns those answers into a price schedule. A survey is worth running only if its answers can change a pricing decision.

## Get the context that changes the answer

If survey responses, a draft questionnaire or past sales are available, look at them first: who answered, how they were reached, the price points asked, and the response rate.

Then ask only what that material cannot answer, and only if the answer would change the research design or the price. Ask at most three questions. Give each one a one-line reason and a default. If the request is urgent, give a first price schedule on stated assumptions and list the questions that would sharpen it.

The questions that usually matter here:

1. **Which prices and options are genuinely on the table?** The survey should test those and nothing else.
2. **Who is the target buyer, and how will they be reached?** A sample of existing fans, staff or friends overstates demand.
3. **What are unit cost and capacity, and is the goal revenue or profit?** Capacity limits can push the best price up.

If there is no answer, assume the goal is profit, capacity is not binding, and stated willingness to pay overstates real purchases.

## Procedure

Where a step names a script and code cannot run here, do the same check by hand on a small case, and say in the deliverable that it was done by hand.

1. **Design for decisions.** Keep only questions whose answers change a decision: purchase likelihood, willingness to pay per option, and the few profile questions needed to weight the sample. Pretest the questionnaire on a handful of target buyers. Budget for the response rate, not the invitations.
2. **Pick the method.**

   | Need | Method |
   |---|---|
   | Quick read on price level for one product | Direct question, or Gabor-Granger: "would you buy at this price?" at several prices |
   | An acceptable price range and signals of "too cheap" | Van Westendorp price sensitivity questions |
   | Trade-offs between features and price across options | Conjoint analysis |
   | Actual behaviour rather than stated intent | A live price test, or historical sales data |

3. **Build cumulative demand.** For each price, the share of respondents willing to pay at least that price. Do this separately for each product, plan or ticket type.
4. **Correct for overstatement.** Stated intent runs high. Count only firm answers in full, discount "probably" answers, weight the sample to the real population, and cross-check against any sales data.
5. **Find the best price.** Expected demand at a price = share willing × market size, capped at capacity. Revenue = price × demand; profit subtracts unit cost. `scripts/wtp_optimal_price.py` builds the table and marks the best price for each type. The most common answer is rarely the best price.
6. **Price several types together.** Price each type on its own curve, then check whether buyers would switch to a cheaper type. When they would, hand over to the pricing-structure-design skill to add fences.
7. **Read the flat top.** Revenue is often nearly flat around the best price. Report the range within a few percent of the maximum, and pick a round or strategic price inside it.
8. **Validate with a small live test** before committing the full schedule.

## Deliverable

**Part A: Price recommendation**, for the decision owner

- The recommended price for each type, and the range that performs almost as well.
- Expected buyers, revenue and profit at that price, with the main uncertainty.
- The live test that would confirm it.

**Part B: Research appendix**, for the analysts

- Sample, response rate, weighting and the overstatement correction used.
- Cumulative demand and revenue tables per type.
- The questionnaire, or the changes recommended to it.

## Traps

- Treating the most popular answer as the best price.
- Surveying existing fans or staff and projecting to the whole market.
- Using non-cumulative shares, so demand at a high price is understated.
- Taking stated willingness to pay at face value.
- Ignoring capacity, so the "best" price sells more seats than exist.
- Anchoring respondents with the order or range of prices shown.
- Pricing each type in isolation when buyers can switch between them.
