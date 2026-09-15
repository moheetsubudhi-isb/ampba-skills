# recommender-build

Use this skill when: Build product, content or next-item recommendations, and choose the method that fits the data: association rules and market basket analysis, item-based or user-based collaborative filtering, content-based similarity, matrix factorisation with ALS, or graph ranking such as PageRank. Use whenever someone wants to recommend products, songs, articles, courses or offers to users; build "customers also bought", "you may also like", "buy again" or "did you forget" features; mine frequent itemsets with support, confidence and lift; turn clicks, views or purchases into implicit ratings; correct for users who rate harshly or generously; handle cold start for new users or new items; or scale item-item similarity for real-time serving. Not for measuring how good an existing recommender is, and not for segmenting customers into groups.

# Recommender build

Act as the data scientist who builds the recommender, and as the advisor who ties every recommendation slot to a business result. A recommendation is only worth showing if it changes what the customer does next.

## Get the context that changes the answer

If interaction data, a catalogue or the current recommendation logic is available, look at it first: number of users and items, interactions per user, share of repeat purchases, and how fast the catalogue changes.

Then ask only what that material cannot answer, and only if the answer would change the method. Ask at most three questions. Give each one a one-line reason and a default. If the request is urgent, build a first version on stated assumptions and list the questions that would sharpen it.

The questions that usually matter here:

1. **Where will the recommendations appear, and what should they drive?** A checkout add-on wants items bought together; a home page wants discovery; an email wants items worth a return visit.
2. **What feedback exists?** Explicit ratings, implicit signals such as views, clicks and purchases, or only baskets without user history. The feedback type narrows the methods.
3. **What must the list respect?** Stock, margin, promotions, items never to recommend, and the time allowed to respond.

If there is no answer, assume implicit purchase data, a "you may also like" slot on product pages, recommendations filtered to in-stock items, and responses that must come back in under a few hundred milliseconds.

## Procedure

Where a step names a script and code cannot run here, do the same check by hand on a small case, and say in the deliverable that it was done by hand.

1. **Define the units.** Decide what a basket is: one order, or all orders in a week. Decide the item level: SKUs change with pack sizes and promotions, so model at a stable product or category level and map back to SKUs.
2. **Build a baseline first:** best sellers overall, best sellers in the user's categories, and "buy again" for repeat categories such as groceries. Every method must beat it.
3. **Choose the method**, then load its reference.

   | Data and goal | Method | Load |
   |---|---|---|
   | Baskets without user history; "bought together"; checkout add-ons | Association rules | `references/association-rules.md` |
   | User-item interactions; "you may also like" | Item-based collaborative filtering, before user-based | `references/collaborative-filtering.md` |
   | Items with rich descriptions or attributes; new items; little interaction data | Content-based similarity | `references/collaborative-filtering.md` |
   | Large, sparse user-item matrix; predicting unseen preferences | Matrix factorisation (ALS) | `references/matrix-factorization.md` |
   | Repeat purchases; ranking the items that anchor a co-purchase network | Graph ranking (PageRank-style) | `references/graph-ranking.md` |

4. **Turn feedback into scores.** Weight signals by strength: purchase above add-to-cart above view above click. Log-scale raw counts. Remember that no interaction is not a dislike.
5. **Correct for rating bias.** Subtract each user's mean rating; use z-scores when users spread ratings differently; subtract each item's mean to remove item popularity bias.
6. **Generate, score, rank, filter.** Generate candidates, score them, rank them, then apply business filters: in stock, not just bought unless the category repeats, allowed by promotions and margin. Diversify so one brand or genre does not fill the list.
7. **Plan cold start.** New users get context-aware best sellers, onboarding choices or content-based picks. New items get content similarity and reserved exposure slots until interactions build up.
8. **Plan serving.** Precompute item-item similarity or factors offline. Online, look up the user's recent items, fetch their neighbours, aggregate and rank. Set a refresh schedule.
9. **Measure before and after launch** with the recommender-evaluation skill.

## Deliverable

**Part A: Recommendation brief**, for the decision owner

- What is recommended, where, and the business result it should move.
- The method chosen, in plain terms, and why it beats the baseline for this slot.
- The cold-start plan, business filters and main risk.

**Part B: Technical appendix**, for the builders

- Data preparation: basket and item definitions, signal weights, bias correction.
- Parameters: minimum support and lift, neighbours, latent factors, regularisation.
- The offline and online pipeline, refresh schedule and filters.

## Traps

- Trusting confidence without lift, so items everyone buys look linked to everything.
- Recommending what the customer just bought, or what is out of stock.
- Treating a missing interaction as a negative rating.
- User-based collaborative filtering across millions of users in real time.
- Rules built on SKUs that disappear when packaging or promotions change.
- A popularity loop in which only best sellers are ever shown, so only they collect data.

---

## Reference: references/association-rules.md

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

---

## Reference: references/collaborative-filtering.md

# Collaborative filtering and content-based similarity

## Feedback

- **Explicit:** ratings, likes, reviews. Clear, but sparse, and one user's 3 stars is not another's.
- **Implicit:** views, clicks, add-to-cart, purchases, watch time. Plentiful but noisy; no click does not mean dislike. Convert to confidence scores, for example by weighting signal types, log-scaling counts, or binning watch share (over 95% watched ≈ strong positive, under 10% ≈ weak).

## User-based collaborative filtering

Find users similar to the target user, then recommend what they liked.
1. Similarity between users: cosine similarity on rating vectors, or Pearson correlation (cosine after mean-centring). Euclidean distance is sensitive to scale and missing values.
2. Take the k nearest neighbours (k is a hyperparameter).
3. Candidates are items neighbours interacted with and the user has not.
4. Score by the neighbours' ratings, weighted by similarity; rank; take the top n.

Struggles at scale (similarity across millions of users) and with users who have little history.

## Item-based collaborative filtering

Find items similar to the ones the user already liked, based on which users interacted with both.
- Item neighbourhoods are more stable than user neighbourhoods and can be precomputed offline into a similar-items table; online serving just looks them up and aggregates. This is how large retailers serve in real time.
- Usually more accurate and scalable than user-based filtering. New items still have a cold-start problem.

## Bias normalisation

- **User bias:** subtract each user's mean rating (mean-centring); use z-scores when users also differ in spread.
- **Item bias:** subtract each item's mean rating, so a blockbuster's general popularity does not dominate.
- Add the biases back when predicting a rating.

## Content-based similarity

Represent items by their attributes or text (category, brand, price band, description via TF-IDF or embeddings) and recommend items similar to those the user liked. Works for new items with no interactions and explains itself ("similar to what you viewed"), but tends to recommend more of the same and misses cross-category tastes. Often blended with collaborative filtering.

---

## Reference: references/graph-ranking.md

# Graph ranking (PageRank-style)

**Use when** items are linked by co-purchase or navigation and the goal is to rank which items matter most in that network: ordering "buy again" and "did you forget" prompts for repeat shoppers, choosing the anchor items for a category, or ranking content by how much other content points to it.

**Idea:** an item is important if important items point to it. Each item passes its importance to the items it links to, split across its links.

**Procedure**
1. Build the graph: nodes are items; an edge from A to B is weighted by how often A and B appear in the same basket for this customer or segment.
2. Normalise each row so outgoing weights sum to 1. This is the transition probability matrix of a Markov chain: the chance of moving from item A to item B.
3. Start with equal ranks for all items.
4. Repeatedly multiply the rank vector by the transition matrix until it stops changing. The result is the steady state.
5. Add a damping factor (commonly 0.85): with a small probability the walk jumps to a random item. This guarantees a steady state even when the graph has dead ends or closed loops.
6. Rank items by steady-state probability. For a customer who bought only some items this time, recommend the highest-ranked items missing from the basket.

**Conditions for a stable answer:** every item reachable from every other, and no fixed-length cycles. Damping enforces both in practice.

**Strengths:** uses the structure of the whole network, not just pairs; simple to compute; explainable as "items most central to your usual shopping".
**Limits:** links must be inferred from co-occurrence; ranks favour hub items such as staples, so filter or down-weight items the customer always buys when discovery is the goal.

---

## Reference: references/matrix-factorization.md

# Matrix factorisation (ALS)

**Use when** the user-item matrix is large and sparse and the goal is to predict preferences for items a user has never seen.

**Idea:** approximate the ratings matrix R (users × items) as the product of a user-factor matrix U (users × f) and an item-factor matrix V (items × f), with f latent factors, usually tens to a few hundred. A predicted rating is the dot product of a user vector and an item vector.

**Alternating least squares**
1. Start V with small random values.
2. Fix V and solve for each user's vector as a regularised least-squares regression on that user's known ratings.
3. Fix U and solve for each item's vector the same way.
4. Repeat until the error on held-out ratings stops falling.

Each step is a ridge regression, so it parallelises well (Spark MLlib, implicit).

**Regularisation:** an L2 penalty (λ) stops large factors from fitting the known ratings tightly and generalising badly. Tune λ and f on a validation split.

**Implicit feedback:** use the confidence-weighted variant, which treats every unobserved pair as a weak negative with low confidence and observed interactions as positives with confidence rising with their count.

**Uses beyond predicted ratings**
- Item-factor vectors give item-item similarity for "similar items".
- User-factor vectors give user neighbourhoods.
- New items gain useful vectors from a handful of interactions, which eases cold start compared with neighbourhood methods, though items with none still need content features.

**Limits:** factors are hard to explain; results depend on λ, f and iterations; retraining is needed as data arrives; users and items with no data still need a fallback.
