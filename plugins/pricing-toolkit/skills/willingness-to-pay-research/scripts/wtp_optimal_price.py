#!/usr/bin/env python3
"""Turn willingness-to-pay responses into demand, revenue and the best price.

Input is one row per respondent with the most they would pay, optionally a
product or ticket type and a survey weight. For each type and candidate price
it computes the share willing to pay at least that price, expected buyers
(scaled to the market, capped at capacity), revenue and profit, and marks the
best price plus every price within --flat of the best.

  python3 wtp_optimal_price.py --csv responses.csv --wtp max_price --type plan \
      --market 20000 --capacity 3000 --cost 4 --calibration 0.6
  python3 wtp_optimal_price.py --selftest
Needs numpy and pandas.
"""
import argparse
import sys

try:
    import numpy as np
    import pandas as pd
except ImportError:
    sys.exit("needs numpy and pandas: pip install numpy pandas")


def schedule(wtp, weights=None, prices=None, market=1.0, capacity=None, cost=0.0, calibration=1.0):
    wtp = np.asarray(wtp, float)
    w = np.ones_like(wtp) if weights is None else np.asarray(weights, float)
    prices = np.unique(wtp) if prices is None else np.asarray(prices, float)
    share = np.array([w[wtp >= p].sum() / w.sum() for p in prices])
    buyers = share * calibration * market
    if capacity is not None:
        buyers = np.minimum(buyers, capacity)
    t = pd.DataFrame({"price": prices, "share_willing": share, "buyers": buyers})
    t["revenue"] = t.price * t.buyers
    t["profit"] = (t.price - cost) * t.buyers
    return t


def best(t, objective="profit", flat=0.03):
    top = t[objective].max()
    t = t.assign(best=t[objective] == top, near_best=t[objective] >= top * (1 - flat))
    return t, t.loc[t[objective].idxmax(), "price"]


def selftest():
    wtp = [10] * 40 + [15] * 10 + [25] * 30 + [40] * 20
    t, p = best(schedule(wtp, market=100), objective="revenue")
    most_common = pd.Series(wtp).mode()[0]
    assert most_common == 10 and p == 25, "the most common answer is not the revenue-maximising price"
    assert abs(t.loc[t.price == 25, "revenue"].item() - 1250) < 1e-9

    t2, p2 = best(schedule(wtp, market=1000, capacity=300), objective="revenue")
    assert p2 == 40, "a capacity cap pushes the best price up"

    t3, p3 = best(schedule(wtp, market=100, cost=12), objective="profit")
    assert p3 in (25, 40) and t3.loc[t3.price == 10, "profit"].item() < 0, "a price below cost can never win"
    assert best(schedule(wtp, market=100, calibration=0.5), "revenue")[1] == 25, "uniform discounting of intent leaves the best price unchanged"
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--csv")
    ap.add_argument("--wtp", help="column with the most each respondent would pay")
    ap.add_argument("--type", help="optional column with product, plan or ticket type")
    ap.add_argument("--weight", help="optional survey weight column")
    ap.add_argument("--prices", nargs="*", type=float, help="candidate prices; default is every distinct answer")
    ap.add_argument("--market", type=float, default=1.0, help="number of potential buyers the sample represents")
    ap.add_argument("--capacity", type=float)
    ap.add_argument("--cost", type=float, default=0.0)
    ap.add_argument("--calibration", type=float, default=1.0, help="share of stated intent expected to buy, e.g. 0.6")
    ap.add_argument("--objective", choices=["profit", "revenue"], default="profit")
    ap.add_argument("--flat", type=float, default=0.03, help="report prices within this share of the best")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not (a.csv and a.wtp):
        ap.error("--csv and --wtp are required")
    df = pd.read_csv(a.csv).dropna(subset=[a.wtp])
    groups = df.groupby(a.type) if a.type else [("all", df)]
    for name, g in groups:
        t, p = best(schedule(g[a.wtp], g[a.weight] if a.weight else None, a.prices, a.market,
                             a.capacity, a.cost, a.calibration), a.objective, a.flat)
        near = t.loc[t.near_best, "price"]
        print(f"\n== {name}: {len(g):,} responses, best {a.objective} at {p:g} "
              f"(within {a.flat:.0%}: {near.min():g} to {near.max():g})")
        print(t.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
