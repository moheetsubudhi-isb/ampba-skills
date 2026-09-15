#!/usr/bin/env python3
"""Mine item-pair association rules with support, confidence, lift and conviction.

Input is a CSV with one row per basket-item: a basket or order ID and an item.
Rules are pairs only (A => B); for larger itemsets use Apriori or FP-Growth.

  python3 basket_rules.py --csv order_items.csv --basket order_id --item product \
      --min-support 0.01 --min-lift 1.2 --top 30
  python3 basket_rules.py --selftest
Needs pandas and numpy.
"""
import argparse
import sys
from itertools import permutations

try:
    import numpy as np
    import pandas as pd
except ImportError:
    sys.exit("needs pandas and numpy: pip install pandas numpy")


def rules(df, basket, item, min_support=0.01):
    onehot = pd.crosstab(df[basket], df[item]).clip(upper=1)
    n = len(onehot)
    support = onehot.mean()
    frequent = support[support >= min_support].index
    m = onehot[frequent].to_numpy()
    pair = (m.T @ m) / n  # support of each item pair
    out = []
    for i, j in permutations(range(len(frequent)), 2):
        s_ab = pair[i, j]
        if s_ab < min_support:
            continue
        conf = s_ab / support[frequent[i]]
        s_b = support[frequent[j]]
        out.append({"antecedent": frequent[i], "consequent": frequent[j], "support": s_ab,
                    "confidence": conf, "lift": conf / s_b,
                    "conviction": np.inf if conf >= 1 else (1 - s_b) / (1 - conf)})
    return pd.DataFrame(out), n


def selftest():
    rng = np.random.default_rng(7)
    rows = []
    for b in range(4000):
        salsa = rng.random() < 0.2
        chips = rng.random() < (0.9 if salsa else 0.1)
        milk = rng.random() < 0.8  # a staple, independent of everything
        # every real basket holds something; a carrier bag keeps empty baskets from vanishing
        rows += [(b, x) for x, keep in [("salsa", salsa), ("chips", chips), ("milk", milk), ("bag", True)] if keep]
    r, _ = rules(pd.DataFrame(rows, columns=["basket", "item"]), "basket", "item", 0.01)
    r = r.set_index(["antecedent", "consequent"])
    staple = r.loc[("salsa", "milk")]
    assert staple.confidence > 0.7, "a staple gets high confidence from any antecedent"
    assert 0.9 < staple.lift < 1.1, "lift exposes that salsa says nothing about milk"
    assert r.loc[("salsa", "chips")].lift > 2.5, "a genuine pairing has high lift"
    assert r.loc[("salsa", "chips")].conviction > 3
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--csv")
    ap.add_argument("--basket", default="basket_id")
    ap.add_argument("--item", default="item")
    ap.add_argument("--min-support", type=float, default=0.01)
    ap.add_argument("--min-lift", type=float, default=1.0)
    ap.add_argument("--top", type=int, default=30)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.csv:
        ap.error("--csv is required")
    df = pd.read_csv(a.csv, usecols=[a.basket, a.item]).dropna().drop_duplicates()
    r, n = rules(df, a.basket, a.item, a.min_support)
    if r.empty:
        sys.exit(f"no pairs reach support {a.min_support} across {n:,} baskets; lower --min-support")
    r = r[r.lift >= a.min_lift].sort_values(["lift", "support"], ascending=False).head(a.top)
    print(f"{n:,} baskets. Lift near 1 means no real link, whatever the confidence.\n")
    print(r.to_string(index=False, float_format=lambda x: f"{x:.3f}"))


if __name__ == "__main__":
    main()
