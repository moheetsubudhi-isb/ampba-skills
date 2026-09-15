#!/usr/bin/env python3
"""Find similar and near-duplicate texts with TF-IDF and cosine similarity.

Lists nearest neighbours for a query (or the first rows), and all pairs above
a duplicate threshold. Compare --analyzer word with --analyzer char: character
n-grams catch spelling variants and codes that word n-grams miss. Neither
catches synonyms; that is the point at which embeddings earn their cost.

  python3 tfidf_similarity.py --csv tickets.csv --text body --id ticket_id --query "card blocked abroad"
  python3 tfidf_similarity.py --csv products.csv --text name --analyzer char --dup-threshold 0.85
  python3 tfidf_similarity.py --selftest
Needs pandas and scikit-learn.
"""
import argparse
import sys

try:
    import numpy as np
    import pandas as pd
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
except ImportError:
    sys.exit("needs pandas and scikit-learn: pip install pandas scikit-learn")


def vectorizer(analyzer):
    if analyzer == "char":
        return TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True, lowercase=True)
    return TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, lowercase=True)


def similarity(texts, analyzer="word"):
    v = vectorizer(analyzer)
    m = v.fit_transform(texts)
    return v, m, cosine_similarity(m)


def duplicates(sim, threshold):
    i, j = np.where(np.triu(sim, k=1) >= threshold)
    return sorted(zip(i, j, sim[i, j]), key=lambda t: -t[2])


def selftest():
    texts = ["refund my order", "refund for my order please", "I want my money back",
             "track my parcel", "colour printer cartridge", "color printer cartridges"]
    _, _, word = similarity(texts, "word")
    _, _, char = similarity(texts, "char")
    assert word[0, 1] > 0.4, "shared words match"
    assert word[0, 2] < 0.15, "a synonym with different words scores near zero: TF-IDF has no meaning"
    assert char[4, 5] > word[4, 5] + 0.2, "character n-grams tolerate spelling variants"
    assert (0, 1, word[0, 1]) in [(a, b, s) for a, b, s in duplicates(word, 0.4)]
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--csv")
    ap.add_argument("--text")
    ap.add_argument("--id")
    ap.add_argument("--analyzer", choices=["word", "char"], default="word")
    ap.add_argument("--query")
    ap.add_argument("--top", type=int, default=5)
    ap.add_argument("--dup-threshold", type=float, default=0.9)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not (a.csv and a.text):
        ap.error("--csv and --text are required")
    df = pd.read_csv(a.csv).dropna(subset=[a.text]).reset_index(drop=True)
    ids = df[a.id] if a.id else df.index
    v, m, sim = similarity(df[a.text].astype(str), a.analyzer)
    print(f"{len(df):,} texts, vocabulary {len(v.vocabulary_):,} ({a.analyzer} n-grams)\n")
    if a.query:
        q = cosine_similarity(v.transform([a.query]), m)[0]
        for i in np.argsort(-q)[:a.top]:
            print(f"{q[i]:.3f}  {ids[i]}  {df[a.text][i][:100]}")
    else:
        for r in range(min(5, len(df))):
            near = [j for j in np.argsort(-sim[r]) if j != r][:a.top]
            print(f"{ids[r]}: {df[a.text][r][:80]}")
            for j in near:
                print(f"    {sim[r, j]:.3f}  {ids[j]}  {df[a.text][j][:80]}")
    pairs = duplicates(sim, a.dup_threshold)
    print(f"\n{len(pairs)} pairs at or above {a.dup_threshold}")
    for i, j, s in pairs[:20]:
        print(f"{s:.3f}  {ids[i]} | {ids[j]}  {df[a.text][i][:50]} || {df[a.text][j][:50]}")


if __name__ == "__main__":
    main()
