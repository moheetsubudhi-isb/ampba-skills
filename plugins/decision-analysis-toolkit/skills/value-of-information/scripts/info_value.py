#!/usr/bin/env python3
"""Value perfect and imperfect information for a payoff-table decision.

Input JSON:
  {"payoffs": {"launch": {"strong": 800, "weak": -300}, "shelve": {"strong": 0, "weak": 0}},
   "prior": {"strong": 0.3, "weak": 0.7},
   "likelihood": {"positive": {"strong": 0.9, "weak": 0.2},
                  "negative": {"strong": 0.1, "weak": 0.8}},
   "cost": 40}
"likelihood" is P(result | outcome); each outcome's column must sum to 1.

Prints the best EMV without information, EVPI, updated probabilities and the
best option for each result, EVSI, efficiency and the buy/skip call.

  python3 info_value.py --input study.json
  python3 info_value.py --selftest
Standard library only.
"""
import argparse
import json


def best_option(payoffs, probs):
    emv = {a: sum(probs[s] * v for s, v in row.items()) for a, row in payoffs.items()}
    a = max(emv, key=emv.get)
    return a, emv[a]


def analyse(payoffs, prior, likelihood=None):
    states = list(prior)
    if abs(sum(prior.values()) - 1) > 1e-6:
        raise ValueError("prior probabilities must sum to 1")
    act, emv = best_option(payoffs, prior)
    ev_perfect = sum(prior[s] * max(row[s] for row in payoffs.values()) for s in states)
    out = {"best_without_info": act, "emv_without_info": emv, "evpi": ev_perfect - emv}
    if likelihood:
        for s in states:
            col = sum(likelihood[r][s] for r in likelihood)
            if abs(col - 1) > 1e-6:
                raise ValueError(f"likelihoods for outcome '{s}' sum to {col:.4f}, not 1")
        results, ev_sample = {}, 0.0
        for r, lik in likelihood.items():
            p_r = sum(lik[s] * prior[s] for s in states)
            if p_r == 0:
                continue
            post = {s: lik[s] * prior[s] / p_r for s in states}
            a, v = best_option(payoffs, post)
            results[r] = {"p_result": p_r, "posterior": post, "best": a, "emv": v}
            ev_sample += p_r * v
        out["by_result"] = results
        out["evsi"] = ev_sample - emv
        out["efficiency"] = out["evsi"] / out["evpi"] if out["evpi"] > 0 else 0.0
    return out


def selftest():
    payoffs = {"launch": {"strong": 800, "weak": -300}, "shelve": {"strong": 0, "weak": 0}}
    prior = {"strong": 0.3, "weak": 0.7}
    good = {"positive": {"strong": 0.9, "weak": 0.2}, "negative": {"strong": 0.1, "weak": 0.8}}
    r = analyse(payoffs, prior, good)
    assert r["best_without_info"] == "launch" and abs(r["emv_without_info"] - 30) < 1e-9
    assert abs(r["evpi"] - 210) < 1e-9
    assert 0 <= r["evsi"] <= r["evpi"], "EVSI can never exceed EVPI"
    assert abs(r["evsi"] - 144) < 1e-9 and r["by_result"]["negative"]["best"] == "shelve"
    assert r["evsi"] < 150, "a study costing 150 has positive EVSI yet is still not worth buying"

    rare = analyse(payoffs, {"strong": 0.02, "weak": 0.98},
                   {"positive": {"strong": 0.95, "weak": 0.05}, "negative": {"strong": 0.05, "weak": 0.95}})
    assert rare["by_result"]["positive"]["posterior"]["strong"] < 0.3, "a 95%-accurate test on a rare event still mostly false-alarms"

    useless = analyse(payoffs, prior, {"positive": {"strong": 0.6, "weak": 0.55}, "negative": {"strong": 0.4, "weak": 0.45}})
    assert abs(useless["evsi"]) < 1e-9, "a study that never changes the decision is worth nothing"
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.input:
        ap.error("--input is required")
    with open(a.input) as fh:
        doc = json.load(fh)
    r = analyse(doc["payoffs"], doc["prior"], doc.get("likelihood"))
    print(f"without information: choose '{r['best_without_info']}', EMV {r['emv_without_info']:,.2f}")
    print(f"EVPI (ceiling on any study): {r['evpi']:,.2f}")
    if "evsi" in r:
        for res, d in r["by_result"].items():
            post = ", ".join(f"{s} {p:.3f}" for s, p in d["posterior"].items())
            print(f"  result '{res}' (p {d['p_result']:.3f}): {post}  -> choose '{d['best']}'")
        print(f"EVSI: {r['evsi']:,.2f}   efficiency {r['efficiency']:.0%}")
        cost = doc.get("cost")
        if cost is not None:
            print(f"study cost {cost:,.2f}: {'buy it' if r['evsi'] > cost else 'skip it'}")


if __name__ == "__main__":
    main()
