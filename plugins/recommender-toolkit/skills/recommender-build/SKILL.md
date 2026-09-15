---
name: recommender-build
description: >-
  Build product, content or next-item recommendations, and choose the method
  that fits the data: association rules and market basket analysis, item-based
  or user-based collaborative filtering, content-based similarity, matrix
  factorisation with ALS, or graph ranking such as PageRank. Use whenever
  someone wants to recommend products, songs, articles, courses or offers to
  users; build "customers also bought", "you may also like", "buy again" or
  "did you forget" features; mine frequent itemsets with support, confidence
  and lift; turn clicks, views or purchases into implicit ratings; correct for
  users who rate harshly or generously; handle cold start for new users or new
  items; or scale item-item similarity for real-time serving. Not for
  measuring how good an existing recommender is, and not for segmenting
  customers into groups.
---

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
