# Association rules (market basket analysis)

**Use when** there are baskets of items bought or used together, with or without user history, and the goal is "bought together", checkout add-ons, bundles, shelf placement or "did you forget" prompts.

**Measures**, for a rule A ⇒ B:
- **Support** = share of baskets containing both A and B. Filters out rare combinations.
- **Confidence** = P(B | A) = support(A and B) / support(A). How often B follows A.
- **Lift** = confidence / support(B). Above 1 means A makes B more likely than chance; about 1 means independent; below 1 means they avoid each other.
- **Conviction** = (1 − support(B)) / (1 − confidence). Above 1 means B depends on A; high values mean the rule rarely fails.

**Why lift matters:** if 80% of baskets contain milk, almost every rule "X ⇒ milk" has confidence near 80% even when X has nothing to do with milk. Lift near 1 exposes this.

**Procedure**
1. Define the basket (one order, or orders in a period) and the item level (category or product, not volatile SKUs).
2. Set minimum support so the itemset count stays manageable. The Apriori principle prunes: an itemset can only be frequent if all its subsets are.
3. Keep rules with lift clearly above 1 and enough support to matter; sort by the business goal (lift for discovery, confidence for add-ons).
4. `scripts/basket_rules.py` computes support, confidence, lift and conviction for item pairs from an order-item CSV.
5. For larger itemsets, use Apriori or FP-Growth in a library such as mlxtend or Spark MLlib.

**Strengths:** easy to explain, built from data every retailer has, no user history needed.
**Limits:** expensive with many items, ignores how much a customer likes an item, not personalised on its own, and rules go stale as ranges change.
