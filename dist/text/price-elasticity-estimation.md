# price-elasticity-estimation

Use this skill when: Measure how sales respond to price and promotions, and turn the answer into a pricing call. Use whenever someone asks for price elasticity or cross-price elasticity; how much volume a price rise or cut will lose or gain; whether a price change will raise revenue or profit; whether customers respond differently when a product is on promotion; whether two products are substitutes or complements; how to fit a log-log demand model on sales and price data; whether a discount pays for itself in extra volume; or how a competitor's price or promotion moves our sales. Not for designing tiers, bundles or segment prices, not for pricing from willingness-to-pay survey data, and not for reading regression coefficients outside a pricing question.

# Price elasticity estimation

Act as the pricing analyst who measures how demand responds to price, and as the advisor who turns that number into a price or promotion decision. An elasticity is only useful once it says whether a price move makes the business richer or poorer.

## Get the context that changes the answer

If sales and price data are available, look at them first: the grain (store-week, SKU-day), how much price actually varies and why, how often promotions run, and whether sales contain zeros or long spikes.

Then ask only what that material cannot answer, and only if the answer would change the estimate or the recommendation. Ask at most three questions. Give each one a one-line reason and a default. If the request is urgent, give a first estimate on stated assumptions and list the questions that would sharpen it.

The questions that usually matter here:

1. **Which decision is this for:** an everyday list price, the depth of a promotion, or a response to a competitor? Each needs a different elasticity.
2. **What moves price in the data?** Promotions, list-price changes, regions or channels. If price only varies during deals, the regular-price elasticity cannot be measured cleanly.
3. **What is the unit margin, and is the goal revenue, profit or volume share?** Revenue and profit often point to different prices.

If there is no answer, assume the goal is profit, promotions are flagged in the data, and gross margin is whatever the cost column implies.

## Procedure

Where a step names a script and code cannot run here, do the same check by hand on a small case, and say in the deliverable that it was done by hand.

1. **Know the data.** Confirm the grain, the share of promotion periods, the range of observed prices, and how zero sales are handled (a log of zero is undefined; drop, aggregate up, or add a small constant and say so).
2. **Fit a log-log demand model:** ln(units) = a + b · ln(price), plus controls for promotions, displays or features, seasonality and store or product effects. The slope b is the own-price elasticity: a 1% price change moves units by b%. Run `scripts/elasticity_fit.py`.
3. **Separate regular and promotional response.** Add a promotion flag and its interaction with ln(price). The regular elasticity is the ln(price) slope; the promotional elasticity adds the interaction. Test the interaction. A pooled model that ignores promotions blends two regimes and usually looks far more elastic than regular-price demand really is, so never set an everyday price from it.
4. **Measure competition.** Add the competitor's ln(price). A positive cross-elasticity means substitutes, a negative one complements. Check for asymmetry, and interact with the competitor's promotion flag: substitution often switches on only when the rival runs a deal.
5. **Read the numbers.**
   - |b| above 1 is elastic: a price cut raises revenue. Below 1 is inelastic: a price rise raises revenue.
   - Revenue is not profit. For constant elasticity above 1 in size, the profit-maximising price is roughly unit cost × b / (1 + b). Use it as a sanity check, not a target.
   - A brand is far more elastic than its category.
   - An interaction that is large but not significant means "not proven", not "no effect".
6. **Price a promotion.** A discount d on gross margin m needs a volume lift of d / (m − d) just to break even; `elasticity_fit.py --breakeven` computes it and compares it with the lift the elasticity predicts. Allow for stockpiling, the dip after the promotion, and sales taken from sister products.
7. **Check causality before betting big.** Prices in historical data respond to demand: retailers promote in peak season and cut prices in weak weeks. That biases elasticities. Where the stakes are high, confirm with a randomised price test or a clean natural experiment.

## Deliverable

**Part A: Pricing brief**, for the decision owner

- Elasticities in plain words: "at regular prices, a 1% rise loses about 2.5% of units."
- The recommendation, with its effect on revenue and profit as a range.
- What is proven, what is not, and the test that would settle it.

**Part B: Technical appendix**, for the analysts

- Model specifications and the coefficient table with standard errors.
- The interaction tests and cross-price results.
- Data notes: grain, exclusions, zero handling, price range observed.

## Traps

- Setting an everyday price from a pooled elasticity that includes promotion weeks.
- Taking the log of zero sales without saying how it was handled.
- Crediting price for a lift that came from the display or advert running alongside the deal.
- Using a category elasticity for one brand, or the reverse.
- Maximising revenue when the business cares about profit.
- Extrapolating far outside the prices ever observed.
- Treating an elasticity from historical data as proven cause and effect.
