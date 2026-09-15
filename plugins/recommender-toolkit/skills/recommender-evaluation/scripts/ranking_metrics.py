#!/usr/bin/env python3
"""Score ranked recommendations, and size an A/B test to detect a lift.

--recs  CSV with user, item, rank (1 = top)
--truth CSV with user, item and optional relevance (graded; default 1)
Reports precision@k, recall@k, hit rate@k, MRR, MAP@k and NDCG@k, averaged per
user then across users, plus catalogue coverage when --catalog-size is given.

  python3 ranking_metrics.py --recs recs.csv --truth test.csv --k 10 --catalog-size 5000
  python3 ranking_metrics.py --sample-size --baseline 0.04 --lift 0.05
  python3 ranking_metrics.py --selftest
Needs pandas and numpy.
"""
import argparse
import math
import sys
from statistics import NormalDist

try:
    import numpy as np
    import pandas as pd
except ImportError:
    sys.exit("needs pandas and numpy: pip install pandas numpy")


def user_metrics(ranked, relevance, k):
    """ranked: items in order; relevance: dict item -> gain (>0 means relevant)."""
    top = ranked[:k]
    hits = [1 if relevance.get(i, 0) > 0 else 0 for i in top]
    n_rel = sum(1 for g in relevance.values() if g > 0)
    precisions = [sum(hits[:p + 1]) / (p + 1) for p, h in enumerate(hits) if h]
    dcg = sum(relevance.get(i, 0) / math.log2(p + 2) for p, i in enumerate(top))
    ideal = sorted((g for g in relevance.values() if g > 0), reverse=True)[:k]
    idcg = sum(g / math.log2(p + 2) for p, g in enumerate(ideal))
    first = next((p for p, h in enumerate(hits) if h), None)
    return {
        "precision@k": sum(hits) / k,
        "recall@k": sum(hits) / n_rel if n_rel else np.nan,
        "hit_rate@k": float(any(hits)),
        "mrr": 1 / (first + 1) if first is not None else 0.0,
        "map@k": sum(precisions) / min(n_rel, k) if n_rel else np.nan,
        "ndcg@k": dcg / idcg if idcg else np.nan,
    }


def evaluate(recs, truth, k):
    rel = truth.groupby("user").apply(lambda g: dict(zip(g["item"], g["relevance"])), include_groups=False)
    rows = []
    for user, g in recs.sort_values("rank").groupby("user"):
        if user in rel.index:
            rows.append(user_metrics(list(g["item"]), rel[user], k))
    return pd.DataFrame(rows).mean(), len(rows)


def sample_size(baseline, relative_lift, alpha=0.05, power=0.8):
    """Users per group for a two-sided two-proportion test."""
    p1, p2 = baseline, baseline * (1 + relative_lift)
    z = NormalDist()
    za, zb = z.inv_cdf(1 - alpha / 2), z.inv_cdf(power)
    pbar = (p1 + p2) / 2
    num = (za * math.sqrt(2 * pbar * (1 - pbar)) + zb * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2
    return math.ceil(num / (p2 - p1) ** 2)


def selftest():
    m = user_metrics(["a", "b", "c", "d", "e"], {"a": 1, "c": 1, "e": 1}, 5)
    assert abs(m["precision@k"] - 0.6) < 1e-9 and m["recall@k"] == 1.0
    assert abs(m["map@k"] - (1 + 2 / 3 + 3 / 5) / 3) < 1e-9
    rel = {"x": 1, "y": 1}
    early = user_metrics(["x", "y", "p", "q", "r"], rel, 5)
    late = user_metrics(["p", "q", "r", "x", "y"], rel, 5)
    assert early["precision@k"] == late["precision@k"], "precision ignores order"
    assert early["ndcg@k"] == 1.0 and late["ndcg@k"] < 0.6, "NDCG rewards putting relevant items first"
    n = sample_size(0.10, 0.03)
    assert 150_000 < n < 170_000, n
    assert sample_size(0.10, 0.10) < n / 8, "a bigger lift needs far fewer users"
    recs = pd.DataFrame({"user": [1] * 5 + [2] * 5, "item": list("abcde") + list("vwxyz"), "rank": [1, 2, 3, 4, 5] * 2})
    truth = pd.DataFrame({"user": [1, 1, 2], "item": ["a", "c", "q"], "relevance": [1, 1, 1]})
    avg, users = evaluate(recs, truth, 5)
    assert users == 2 and abs(avg["precision@k"] - 0.2) < 1e-9, "macro average across users"
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--recs")
    ap.add_argument("--truth")
    ap.add_argument("--k", type=int, default=10)
    ap.add_argument("--catalog-size", type=int)
    ap.add_argument("--sample-size", action="store_true")
    ap.add_argument("--baseline", type=float, help="baseline conversion rate, e.g. 0.04")
    ap.add_argument("--lift", type=float, help="relative lift to detect, e.g. 0.05 for +5%%")
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--power", type=float, default=0.8)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.sample_size:
        if a.baseline is None or a.lift is None:
            ap.error("--sample-size needs --baseline and --lift")
        n = sample_size(a.baseline, a.lift, a.alpha, a.power)
        print(f"{n:,} users per group to detect {a.baseline:.2%} -> {a.baseline * (1 + a.lift):.2%} "
              f"(alpha {a.alpha}, power {a.power})")
        return
    if not (a.recs and a.truth):
        ap.error("--recs and --truth are required")
    recs = pd.read_csv(a.recs)
    truth = pd.read_csv(a.truth)
    if "relevance" not in truth:
        truth["relevance"] = 1
    avg, users = evaluate(recs, truth, a.k)
    print(f"{users:,} users with both recommendations and test interactions, k = {a.k}\n")
    print(avg.round(4).to_string())
    if a.catalog_size:
        print(f"coverage           {recs['item'].nunique() / a.catalog_size:.2%} of the catalogue")


if __name__ == "__main__":
    main()
