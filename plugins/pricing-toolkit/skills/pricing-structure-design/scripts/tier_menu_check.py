#!/usr/bin/env python3
"""Check whether a price menu makes each segment choose the option meant for it.

Each segment picks the option with the highest surplus (value minus price),
or nothing if every surplus is negative; ties go to the higher-priced option.
Reports each segment's choice, flags segments that trade down from their
intended option, and totals revenue and profit. --sweep varies one option's
price to show where the menu stops cannibalising.

Menu JSON:
  {"options":  {"basic": {"price": 45, "cost": 5}, "pro": {"price": 140, "cost": 15}},
   "segments": [{"name": "small teams", "size": 100, "intended": "basic",
                 "values": {"basic": 50, "pro": 60}},
                {"name": "power users", "size": 40, "intended": "pro",
                 "values": {"basic": 70, "pro": 150}}]}

  python3 tier_menu_check.py --menu menu.json
  python3 tier_menu_check.py --menu menu.json --sweep pro 80 160 10
  python3 tier_menu_check.py --selftest
Standard library only.
"""
import argparse
import json


def evaluate(menu):
    opts = menu["options"]
    rows, revenue, profit = [], 0.0, 0.0
    for s in menu["segments"]:
        surplus = {o: s["values"].get(o, 0) - opts[o]["price"] for o in opts}
        choice = max(surplus, key=lambda o: (surplus[o], opts[o]["price"]))
        if surplus[choice] < 0:
            choice = None
        intended = s.get("intended")
        rows.append({"segment": s["name"], "size": s["size"], "choice": choice, "intended": intended,
                     "surplus": {o: round(v, 2) for o, v in surplus.items()},
                     "cannibalised": bool(intended and choice != intended)})
        if choice:
            revenue += s["size"] * opts[choice]["price"]
            profit += s["size"] * (opts[choice]["price"] - opts[choice].get("cost", 0))
    return rows, revenue, profit


def sweep(menu, option, lo, hi, step):
    out, p = [], lo
    while p <= hi + 1e-9:
        m = json.loads(json.dumps(menu))
        m["options"][option]["price"] = p
        rows, rev, prof = evaluate(m)
        out.append((p, rev, prof, sum(r["cannibalised"] for r in rows)))
        p += step
    return out


def selftest():
    menu = {"options": {"basic": {"price": 45, "cost": 5}, "pro": {"price": 140, "cost": 15}},
            "segments": [{"name": "small", "size": 100, "intended": "basic", "values": {"basic": 50, "pro": 60}},
                         {"name": "power", "size": 40, "intended": "pro", "values": {"basic": 70, "pro": 150}}]}
    rows, rev, prof = evaluate(menu)
    power = next(r for r in rows if r["segment"] == "power")
    assert power["choice"] == "basic" and power["cannibalised"], "an overpriced premium tier makes its best buyers trade down"
    menu["options"]["pro"]["price"] = 110
    rows2, rev2, prof2 = evaluate(menu)
    assert all(not r["cannibalised"] for r in rows2) and prof2 > prof, "a lower premium price earns more by keeping the segment"
    best = max(sweep(menu, "pro", 80, 160, 5), key=lambda t: t[2])
    assert best[0] == 125 and best[3] == 0, "the most profitable premium price is the highest one that still self-selects"
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--menu")
    ap.add_argument("--sweep", nargs=4, metavar=("OPTION", "LOW", "HIGH", "STEP"))
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.menu:
        ap.error("--menu is required")
    with open(a.menu) as fh:
        menu = json.load(fh)
    rows, rev, prof = evaluate(menu)
    for r in rows:
        flag = "  <- trades down from " + r["intended"] if r["cannibalised"] else ""
        print(f"{r['segment']:<20} size {r['size']:>6}  chooses {str(r['choice']):<12} surplus {r['surplus']}{flag}")
    print(f"\nrevenue {rev:,.2f}   profit {prof:,.2f}")
    if a.sweep:
        opt, lo, hi, step = a.sweep[0], float(a.sweep[1]), float(a.sweep[2]), float(a.sweep[3])
        print(f"\nprice of {opt}   revenue   profit   segments trading down")
        for p, r, pr, c in sweep(menu, opt, lo, hi, step):
            print(f"{p:>10g} {r:>10,.0f} {pr:>8,.0f} {c:>8}")


if __name__ == "__main__":
    main()
