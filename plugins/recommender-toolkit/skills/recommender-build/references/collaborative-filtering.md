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
