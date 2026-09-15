# text-and-embedding-features

Use this skill when: Turn text into numbers for search, matching, deduplication, classification or clustering, and choose between TF-IDF, embeddings and simpler methods. Use whenever someone asks how to find similar tickets, products, documents, CVs or reviews by their text; detect near-duplicate records from names, addresses or descriptions; build TF-IDF vectors, n-grams or stop-word lists; choose word, sentence or document embeddings (word2vec, GloVe, fastText, sentence transformers or a hosted embedding API); decide whether embeddings are worth the cost over TF-IDF; handle tokenisation, subwords, spelling variants or several languages; measure cosine similarity; or store and search vectors for semantic search. Not for choosing how to cluster the resulting vectors into segments, and not for encoding ordinary categorical columns.

# Text and embedding features

Act as the data scientist who represents text so a machine can compare it, and as the advisor who picks the cheapest representation that does the job. Embeddings are not always better; they are always more expensive.

## Get the context that changes the answer

If sample text, existing matches or a labelled set of similar pairs is available, look at it first: text length, vocabulary, codes and jargon, languages and duplicates.

Then ask only what that material cannot answer, and only if the answer would change the representation. Ask at most three questions. Give each one a one-line reason and a default. If the request is urgent, build a first version on stated assumptions and list the questions that would sharpen it.

The questions that usually matter here:

1. **What counts as similar: the same words, or the same meaning?** Matching product codes needs exact terms; matching "refund" with "money back" needs meaning.
2. **How much text, how long, in which languages, and how much jargon?** This decides between word n-grams, character n-grams and embedding models.
3. **Can the text leave the company, and do matches need explaining?** Hosted embedding APIs may be ruled out; TF-IDF matches can be explained by shared terms.

If there is no answer, assume short English text, meaning matters, data must stay in-house, and a TF-IDF baseline is compared with a locally run sentence-embedding model.

## Procedure

Where a step names a script and code cannot run here, do the same check by hand on a small case, and say in the deliverable that it was done by hand.

1. **Clean lightly.** Lower-case, normalise whitespace, strip boilerplate such as signatures and templates. Keep numbers and codes when they carry meaning.
2. **Build a TF-IDF baseline.** Words that are frequent in a document but rare across the collection get the most weight.
   - Word unigrams and bigrams, sublinear term frequency, a minimum document frequency to drop typos, a maximum to drop near-universal words.
   - Character 3–5-grams for spelling variants, names, addresses and product codes.
   - Remove stop words for topic matching, but keep them for sentiment and short text, where "not" changes the meaning.
3. **Measure it** with `scripts/tfidf_similarity.py`. It lists each record's nearest neighbours, near-duplicate pairs above a threshold, and compares word and character n-grams.
4. **Decide whether embeddings are needed.**
   - **Move to embeddings** when synonyms and paraphrases matter (TF-IDF scores "refund" and "money back" as unrelated), texts are short and share few words, or several languages are mixed.
   - **Stay with TF-IDF** when exact terms and codes decide a match, explanations are required, or the budget is small.
   - **Combine both** scores when exact terms and meaning both matter.
5. **Pick the embedding level.** Word vectors (word2vec, GloVe, fastText) are cheap, but averaging them over a sentence loses word order; fastText copes with unseen words through subword pieces. Sentence embeddings suit sentences and paragraphs. Split long documents into chunks. Check a public benchmark for the language and domain, then test on your own data.
6. **Evaluate on labelled pairs.** Mark 50–200 pairs as similar or not, then compare TF-IDF, embeddings and the combination by precision among the top matches.
7. **Serve.** Normalise vectors and use cosine similarity. Exact search is fine up to a few hundred thousand items; use an approximate nearest-neighbour index beyond that. Re-embed everything when the model changes.
8. **For grouping the vectors into segments,** hand over to the clustering-and-segmentation skill, reducing dimensions first if needed.

## Deliverable

**Part A: Matching brief**, for the decision owner

- The method chosen and why, in plain terms.
- Match quality on the labelled sample, with examples of good matches and misses.
- Cost, speed and privacy implications.

**Part B: Technical appendix**, for the builders

- Preprocessing, n-gram settings or the embedding model and version.
- The evaluation table across methods.
- The index design and the re-embedding plan.

## Traps

- Removing stop words such as "not", "no" and "without" that carry meaning.
- Fitting the TF-IDF vocabulary on test documents while evaluating a classifier.
- Mixing vectors from two embedding models or model versions in one index.
- Judging similarity by eyeballing three examples.
- Sending confidential text to an external API without approval.
- Averaging word vectors over long documents until everything looks alike.
