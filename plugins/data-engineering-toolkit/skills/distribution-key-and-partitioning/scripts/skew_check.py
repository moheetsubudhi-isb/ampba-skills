#!/usr/bin/env python3
"""Check how evenly candidate distribution keys spread rows across nodes.

Hashes each value of each candidate column into N buckets, the way hash
distribution does, and reports rows per node, the max-to-mean ratio, the NULL
share, the number of distinct values and the largest values' shares. Real
warehouses use their own hash functions, so read the ratio as a guide to the
key's shape, not an exact forecast of any platform.

  python3 skew_check.py --csv orders_sample.csv --columns customer_id status region --nodes 16
  python3 skew_check.py --selftest
Needs pandas.
"""
import argparse
import hashlib
import sys

try:
    import pandas as pd
except ImportError:
    sys.exit("needs pandas: pip install pandas")


def bucket(value, nodes):
    if pd.isna(value):
        return 0  # every NULL hashes to the same place
    return int(hashlib.md5(str(value).encode()).hexdigest(), 16) % nodes


def skew(series, nodes, top=3):
    counts = series.map(lambda v: bucket(v, nodes)).value_counts().reindex(range(nodes), fill_value=0)
    shares = series.value_counts(normalize=True, dropna=False).head(top)
    return {
        "rows": len(series),
        "distinct": int(series.nunique(dropna=True)),
        "null_share": float(series.isna().mean()),
        "max_to_mean": float(counts.max() / counts.mean()),
        "empty_nodes": int((counts == 0).sum()),
        "top_values": ", ".join(f"{k}={v:.1%}" for k, v in shares.items()),
    }


def verdict(r):
    if r["max_to_mean"] < 1.2:
        return "even"
    if r["max_to_mean"] < 2:
        return "watch"
    return "skewed"


def selftest():
    n, nodes = 50_000, 16
    ids = pd.Series(range(n)).astype(str)
    status = pd.Series(["NEW", "SHIPPED", "SHIPPED", "DELIVERED"] * (n // 4))
    fk = pd.Series([None if i % 5 < 2 else f"c{i}" for i in range(n)])
    assert skew(ids, nodes)["max_to_mean"] < 1.1, "a unique ID spreads evenly"
    s = skew(status, nodes)
    assert s["max_to_mean"] > 3 and s["empty_nodes"] >= nodes - 3, "a status column leaves most nodes idle"
    f = skew(fk, nodes)
    assert f["null_share"] >= 0.39 and f["max_to_mean"] > 5, "40% NULLs pile onto one node"
    assert verdict(skew(ids, nodes)) == "even" and verdict(s) == "skewed"
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--csv")
    ap.add_argument("--columns", nargs="+")
    ap.add_argument("--nodes", type=int, default=8)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not (a.csv and a.columns):
        ap.error("--csv and --columns are required")
    df = pd.read_csv(a.csv, usecols=a.columns, dtype=str, keep_default_na=True)
    rows = {c: {**skew(df[c], a.nodes), "verdict": None} for c in a.columns}
    for r in rows.values():
        r["verdict"] = verdict(r)
    table = pd.DataFrame(rows).T.sort_values("max_to_mean")
    print(f"{len(df):,} rows across {a.nodes} nodes. Ratio under 1.2 is healthy; above 2 needs another key.\n")
    print(table.to_string(float_format=lambda x: f"{x:.2f}"))


if __name__ == "__main__":
    main()
