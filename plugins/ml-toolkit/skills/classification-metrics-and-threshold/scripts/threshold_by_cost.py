#!/usr/bin/env python3
"""Pick a classifier threshold from error costs, review capacity or a recall target.

Input is a CSV of true labels (0/1) and model scores. Reports the base rate,
ROC-AUC and PR-AUC, then precision, recall and expected cost at: 0.5, the
cost-minimising threshold, the capacity threshold and the recall target.

  python3 threshold_by_cost.py --csv scored.csv --label y_true --score y_score \
      --cost-fp 1 --cost-fn 50 --capacity 300 --min-recall 0.9
  python3 threshold_by_cost.py --selftest
Needs numpy, pandas and scikit-learn.
"""
import argparse
import sys

try:
    import numpy as np
    import pandas as pd
    from sklearn.metrics import average_precision_score, roc_auc_score
except ImportError:
    sys.exit("needs numpy, pandas and scikit-learn: pip install numpy pandas scikit-learn")


def curve(y, s):
    """Counts when flagging every score >= each distinct threshold, highest first."""
    order = np.argsort(-s, kind="mergesort")
    s_sorted, y_sorted = s[order], y[order]
    last = np.r_[np.nonzero(np.diff(s_sorted))[0], len(s) - 1]
    tp = np.cumsum(y_sorted)[last]
    fp = np.cumsum(1 - y_sorted)[last]
    return pd.DataFrame({"threshold": np.r_[np.inf, s_sorted[last]], "flagged": np.r_[0, last + 1],
                         "tp": np.r_[0, tp], "fp": np.r_[0, fp]})


def with_metrics(t, positives, cost_fp, cost_fn):
    t = t.copy()
    t["fn"] = positives - t.tp
    t["precision"] = np.where(t.flagged > 0, t.tp / t.flagged.clip(lower=1), np.nan)
    t["recall"] = t.tp / positives
    t["expected_cost"] = t.fp * cost_fp + t.fn * cost_fn
    return t


def pick(y, s, cost_fp, cost_fn, capacity=None, min_recall=None):
    positives = int(y.sum())
    t = with_metrics(curve(y, s), positives, cost_fp, cost_fn)
    rows = {"cost-minimising": t.loc[t.expected_cost.idxmin()]}
    at_half = t[t.threshold >= 0.5]
    rows["default 0.5"] = at_half.iloc[-1] if len(at_half) else t.iloc[0]
    if capacity is not None:
        rows[f"capacity {capacity}"] = t[t.flagged <= capacity].iloc[-1]
    if min_recall is not None:
        ok = t[t.recall >= min_recall]
        if len(ok):
            rows[f"recall >= {min_recall:.0%}"] = ok.iloc[0]
    return pd.DataFrame(rows).T, {"base_rate": positives / len(y), "roc_auc": roc_auc_score(y, s),
                                  "pr_auc": average_precision_score(y, s)}


def selftest():
    rng = np.random.default_rng(0)
    n = 20_000
    y = (rng.random(n) < 0.02).astype(int)
    z = rng.normal(np.where(y == 1, 2.0, 0.0), 1.0)
    s = 1 / (1 + np.exp(-(z - 2.5)))
    table, summary = pick(y, s, cost_fp=1, cost_fn=50, capacity=500, min_recall=0.9)
    assert summary["roc_auc"] > 0.85, "scores separate classes"
    assert summary["pr_auc"] < summary["roc_auc"] - 0.3, "PR-AUC exposes rare positives that ROC-AUC flatters"
    assert table.loc["cost-minimising", "threshold"] < 0.5, "expensive misses push the threshold down"
    assert table.loc["cost-minimising", "expected_cost"] < table.loc["default 0.5", "expected_cost"]
    assert table.loc["capacity 500", "flagged"] <= 500
    assert table.loc["recall >= 90%", "recall"] >= 0.9
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--csv")
    ap.add_argument("--label", default="y_true")
    ap.add_argument("--score", default="y_score")
    ap.add_argument("--cost-fp", type=float, default=1.0)
    ap.add_argument("--cost-fn", type=float, default=1.0)
    ap.add_argument("--capacity", type=int)
    ap.add_argument("--min-recall", type=float)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.csv:
        ap.error("--csv is required")
    df = pd.read_csv(a.csv).dropna(subset=[a.label, a.score])
    y, s = df[a.label].to_numpy(), df[a.score].to_numpy(dtype=float)
    if not set(np.unique(y)) <= {0, 1}:
        ap.error(f"{a.label} must contain only 0 and 1")
    table, summary = pick(y.astype(int), s, a.cost_fp, a.cost_fn, a.capacity, a.min_recall)
    print(f"base rate {summary['base_rate']:.2%}   ROC-AUC {summary['roc_auc']:.3f}   PR-AUC {summary['pr_auc']:.3f}")
    print(f"costs: false positive {a.cost_fp}, false negative {a.cost_fn}\n")
    cols = ["threshold", "flagged", "tp", "fp", "fn", "precision", "recall", "expected_cost"]
    print(table[cols].astype(float).round(4).to_string())


if __name__ == "__main__":
    main()
