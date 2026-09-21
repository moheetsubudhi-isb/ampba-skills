# pricing-structure-design

Use this skill when: Design how prices differ across customers, versions and bundles so more value is captured without the low price leaking to everyone. Always use this skill to diagnose a product line's price ladder, gaps or margins; when discounting has eroded realised margins or pushed lines into loss; when asked whether volume, bulk or quantity discounts make sense; and for the fairness or legal risk of charging different people different prices, including personalised or dynamic pricing. Also use it for segment prices, good-better-best tiers, versioning, bundles, two-part tariffs, peak and off-peak or regional prices and student or loyalty discounts; how to structure plans and the gaps between them; why customers keep choosing the cheaper tier; and what fences stop a discount leaking. Not for estimating elasticity from sales data, not for running a willingness-to-pay survey, and not for sharing out scarce supply fairly.

# Pricing structure design

Act as the pricing strategist who decides how prices should differ, and as the advisor who makes sure the structure holds up once customers start choosing. A price menu works only if each kind of customer prefers the option meant for them.

## Get the context that changes the answer

If a price list, plan menu, sales by tier or discount history is available, look at it first: current tiers and prices, take-up by tier, list versus realised prices, and who buys what.

Then ask only what that material cannot answer, and only if the answer would change the structure. Ask at most three questions. Give each one a one-line reason and a default. If the request is urgent, give a first structure on stated assumptions and list the questions that would sharpen it.

The questions that usually matter here:

1. **Which customers value the product differently, and how can you tell them apart?** An observable signal (student, region, time) allows group prices; without one, customers must sort themselves through a menu.
2. **Can low-price buyers resell, share or pretend to be another group?** If they can, the structure leaks.
3. **What matters besides margin?** Market share, brand, regulation, and how customers will perceive fairness.

If there is no answer, assume no reliable signal, so a self-selection menu is needed, resale is hard, and fairness risk must be reviewed before any personalised price.

## Procedure

Where a step names a script and code cannot run here, do the same check by hand on a small case, and say in the deliverable that it was done by hand.

1. **Check the three prerequisites.** Market power (the business sets its price), a way to separate buyers by what they will pay, and no easy resale between groups. If one fails, differentiated pricing will not hold; say so and stop.
2. **Pick the mechanism.**

   | How buyers are separated | Mechanism | Examples |
   |---|---|---|
   | Individually | Negotiation, auctions, personalised offers | Enterprise deals, B2B quotes |
   | By their own choice from a menu | Tiers and versions, volume discounts, bundles, two-part tariffs | Free / Pro / Enterprise; bulk packs; fee plus usage |
   | By an observable group signal | Student, senior, regional, peak and off-peak, channel, loyalty prices | Matinee tickets, app-only prices |

   The rule underneath all three: the less price-sensitive group pays more.
3. **Build fences** that keep groups apart: time (advance purchase, off-peak), identity (student ID, verified business), geography or channel, and deliberately limited versions. Estimate how much leaks through each one.
4. **Test the menu for self-selection.** For each segment, value minus price must be highest on its intended option. Run `scripts/tier_menu_check.py` with segment sizes, their values for each option, and the prices. When high-value buyers trade down, widen the value gap (strip features from the lower tier) or narrow the price gap.
5. **Diagnose the product line.** Map the price ladder within each line (lowest to highest price, the gaps between rungs), compare margin at list price with realised margin after discounts, find lines that discounting has pushed below zero, and see which tier carries the revenue. This diagnoses the structure; setting optimal gaps needs demand or willingness-to-pay data.
6. **Consider bundles** when customers value the items differently in offsetting ways. Mixed bundling, which also sells items separately, usually beats pure bundling.
7. **Review fairness, law and trust.** Never price on protected attributes. Be ready to explain every price difference in plain terms. Dynamic and personalised pricing draw the sharpest backlash.
8. **Pilot and measure** take-up by tier, upgrades and downgrades, leakage through fences, and realised margin.

## Deliverable

**Part A: Structure brief**, for the decision owner

- The proposed structure in one table: option or group · price · who it is for · fence.
- Expected effect on margin and volume, and the main leakage or cannibalisation risk.
- The fairness position, and the pilot plan.

**Part B: Design appendix**, for the analysts

- The self-selection check per segment, with surplus on each option.
- The product-line diagnosis: ladders, list and realised margins, discount erosion.
- Assumptions about segment sizes and values, and how to test them.

## Traps

- Pricing the premium tier so high that its best customers trade down.
- A basic tier so generous that nobody needs the upgrade.
- A discount with no fence, so every customer claims it.
- Separating groups on a signal that cannot be verified.
- Discount creep that quietly turns profitable lines into loss-makers.
- Judging tiers by revenue when margin tells a different story.
- Personalised prices based on sensitive attributes.
