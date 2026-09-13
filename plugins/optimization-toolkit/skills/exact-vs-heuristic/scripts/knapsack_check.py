#!/usr/bin/env python3
"""Compare greedy rules with the exact optimum on a small knapsack.

Shows two lessons: the greedy rule matters, and even a good greedy rule gives
no guarantee, so always report the gap to a known optimum or bound.

  python3 knapsack_check.py --capacity 10 --item P:12:6 --item Q:9:5 --item R:9:5
  python3 knapsack_check.py --selftest
Items are name:value:weight with whole-number weights.
"""
import argparse
import sys


def exact(items, cap):
    """Dynamic programme over capacity; fine for small integer weights."""
    if len(items) * (cap + 1) > 5_000_000:
        raise SystemExit("instance too large for the exact check")
    best = [[0] * (cap + 1) for _ in range(len(items) + 1)]
    for i, (_, v, w) in enumerate(items, 1):
        for c in range(cap + 1):
            best[i][c] = best[i - 1][c]
            if w <= c and best[i - 1][c - w] + v > best[i][c]:
                best[i][c] = best[i - 1][c - w] + v
    chosen, c = [], cap
    for i in range(len(items), 0, -1):
        if best[i][c] != best[i - 1][c]:
            name, _, w = items[i - 1]
            chosen.append(name)
            c -= w
    return best[-1][cap], sorted(chosen)


def greedy(items, cap, key):
    total, room, chosen = 0, cap, []
    for name, v, w in sorted(items, key=key, reverse=True):
        if w <= room:
            total, room = total + v, room - w
            chosen.append(name)
    return total, sorted(chosen)


RULES = {
    "greedy: highest value first": lambda it: it[1],
    "greedy: highest value per weight": lambda it: it[1] / it[2],
}


def compare(items, cap):
    results = {rule: greedy(items, cap, key) for rule, key in RULES.items()}
    results["exact optimum"] = exact(items, cap)
    return results


def selftest():
    r = compare([("A", 10, 10), ("B", 6, 4), ("C", 6, 4), ("D", 5, 2)], 10)
    value, ratio, opt = (r[k][0] for k in (*RULES, "exact optimum"))
    assert value < ratio == opt == 17, "ratio rule beats value rule here"
    r = compare([("P", 12, 6), ("Q", 9, 5), ("R", 9, 5)], 10)
    ratio, opt = r["greedy: highest value per weight"][0], r["exact optimum"][0]
    assert ratio == 12 and opt == 18, "even the better greedy rule can miss badly"
    print("selftest ok")


def parse_item(text):
    name, v, w = text.split(":")
    if int(w) <= 0 or int(v) < 0:
        raise argparse.ArgumentTypeError("value must be >= 0 and weight > 0")
    return name, int(v), int(w)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--capacity", type=int)
    ap.add_argument("--item", type=parse_item, action="append", default=[])
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.capacity is None or a.capacity < 0 or not a.item:
        ap.error("give --capacity and at least one --item name:value:weight")
    results = compare(a.item, a.capacity)
    opt = results["exact optimum"][0]
    for rule, (total, chosen) in results.items():
        gap = f"{(opt - total) / opt:.1%} below optimum" if opt else "n/a"
        print(f"{rule:34} value {total:6}  gap {gap:18}  items {chosen}")


if __name__ == "__main__":
    main()
