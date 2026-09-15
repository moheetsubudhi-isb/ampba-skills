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
