#!/usr/bin/env python3
"""Fold back a decision tree by expected monetary value, and sweep a probability.

Tree JSON. A node is one of:
  {"decision": "name", "options": {"label": node, ...}}
  {"chance": "name", "outcomes": [{"label": "...", "p": 0.4, "node": node}, ...]}
  {"payoff": 1200000}
A chance outcome's "p" may be a parameter name (e.g. "p_success"), and
"1-p_success" is allowed; set parameters under "params" at the top level:
  {"params": {"p_success": 0.4}, "tree": node}

Prints the EMV, the best choice at every decision, and the risk profile of the
best strategy. --sweep PARAM LOW HIGH STEPS shows where the root choice flips.

  python3 decision_tree.py --tree launch.json
  python3 decision_tree.py --tree launch.json --sweep p_success 0 1 21
  python3 decision_tree.py --selftest
Standard library only.
"""
import argparse
import json
from collections import defaultdict


def prob(p, params):
    if isinstance(p, (int, float)):
        return float(p)
    if p.startswith("1-"):
        return 1 - float(params[p[2:]])
    return float(params[p])


def fold(node, params):
    """Return (emv, policy dict, risk profile {payoff: probability})."""
    if "payoff" in node:
        return float(node["payoff"]), {}, {float(node["payoff"]): 1.0}
    if "chance" in node:
        ps = [prob(o["p"], params) for o in node["outcomes"]]
        if abs(sum(ps) - 1) > 1e-6:
            raise ValueError(f"probabilities at chance node '{node['chance']}' sum to {sum(ps):.4f}")
        emv, policy, profile = 0.0, {}, defaultdict(float)
        for o, p in zip(node["outcomes"], ps):
            v, pol, prof = fold(o["node"], params)
            emv += p * v
            policy.update(pol)
            for x, q in prof.items():
                profile[x] += p * q
        return emv, policy, dict(profile)
    best = None
    for label, child in node["options"].items():
        v, pol, prof = fold(child, params)
        if best is None or v > best[0]:
            best = (v, label, pol, prof)
    v, label, pol, prof = best
    return v, {node["decision"]: label, **pol}, prof


def sweep(doc, param, lo, hi, steps):
    rows = []
    for i in range(steps):
        x = lo + (hi - lo) * i / max(steps - 1, 1)
        params = {**doc.get("params", {}), param: x}
        emv, policy, _ = fold(doc["tree"], params)
        rows.append((x, emv, policy[doc["tree"]["decision"]]))
    return rows


def selftest():
    doc = {"params": {"p_high": 0.5},
           "tree": {"decision": "launch?", "options": {
               "launch": {"chance": "demand", "outcomes": [
                   {"label": "high", "p": "p_high", "node": {"payoff": 500}},
                   {"label": "low", "p": "1-p_high", "node": {"payoff": -200}}]},
               "license": {"payoff": 100},
               "do nothing": {"payoff": 0}}}}
    emv, policy, profile = fold(doc["tree"], doc["params"])
    assert abs(emv - 150) < 1e-9 and policy["launch?"] == "launch"
    assert abs(profile[-200.0] - 0.5) < 1e-9, "the best strategy still loses money half the time"
    flips = sweep(doc, "p_high", 0, 1, 101)
    first_launch = next(x for x, _, c in flips if c == "launch")
    assert abs(first_launch - 0.43) < 0.011, "launch beats licensing once p_high passes 300/700"

    robust = {"params": {"q": 0.5}, "tree": {"decision": "d", "options": {
        "a": {"chance": "c", "outcomes": [{"label": "x", "p": "q", "node": {"payoff": 90}},
                                          {"label": "y", "p": "1-q", "node": {"payoff": 60}}]},
        "b": {"payoff": 50}}}}
    assert {c for _, _, c in sweep(robust, "q", 0, 1, 11)} == {"a"}, "a decision that never flips is robust"
    try:
        fold({"chance": "bad", "outcomes": [{"label": "x", "p": 0.6, "node": {"payoff": 1}},
                                            {"label": "y", "p": 0.6, "node": {"payoff": 0}}]}, {})
        raise AssertionError("probabilities over 1 must be rejected")
    except ValueError:
        pass
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tree")
    ap.add_argument("--sweep", nargs=4, metavar=("PARAM", "LOW", "HIGH", "STEPS"))
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.tree:
        ap.error("--tree is required")
    with open(a.tree) as fh:
        doc = json.load(fh)
    if "tree" not in doc:
        doc = {"params": {}, "tree": doc}
    emv, policy, profile = fold(doc["tree"], doc.get("params", {}))
    print(f"EMV of best strategy: {emv:,.2f}")
    for d, choice in policy.items():
        print(f"  at '{d}': {choice}")
    print("\nrisk profile (payoff: probability)")
    for x in sorted(profile):
        print(f"  {x:>14,.2f}: {profile[x]:.3f}")
    print(f"  chance of a loss: {sum(q for x, q in profile.items() if x < 0):.3f}")
    if a.sweep:
        param, lo, hi, steps = a.sweep[0], float(a.sweep[1]), float(a.sweep[2]), int(a.sweep[3])
        if doc["tree"].get("decision") is None:
            ap.error("--sweep needs a decision node at the root")
        print(f"\n{param:>10}  EMV            root choice")
        prev = None
        for x, v, c in sweep(doc, param, lo, hi, steps):
            mark = "  <- flips" if prev is not None and c != prev else ""
            print(f"{x:>10.3f}  {v:>13,.2f}  {c}{mark}")
            prev = c


if __name__ == "__main__":
    main()
