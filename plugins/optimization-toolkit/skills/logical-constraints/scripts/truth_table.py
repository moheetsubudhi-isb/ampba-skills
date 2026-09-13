#!/usr/bin/env python3
"""Prove that constraints encode a business rule, by trying every case.

--given   situation variables; every combination is tried
--decide  variables the model chooses
Variables are binary unless written name=lo..hi (small integer range).

Without --sense, every assignment the constraints allow must satisfy the rule,
and a situation may be infeasible only when the rule allows nothing.
With --sense max|min --target v, only the assignments an optimiser would pick
(best v) must satisfy the rule, which exposes direction-dependent formulations.

  python3 truth_table.py --given a b --decide c \
      --constraint "c <= a" --constraint "c <= b" --rule "c == (a and b)" \
      --sense max --target c
  python3 truth_table.py --selftest

Expressions run through eval(); pass only expressions you wrote yourself.
"""
import argparse
import itertools
import sys

SAFE = {"__builtins__": {}, "min": min, "max": max, "abs": abs}


def domains(specs):
    out = []
    for spec in specs:
        if "=" in spec:
            name, rng = spec.split("=", 1)
            lo, hi = (int(v) for v in rng.split(".."))
            out.append((name, range(lo, hi + 1)))
        else:
            out.append((spec, (0, 1)))
    return out


def holds(exprs, env):
    return all(eval(e, SAFE, dict(env)) for e in exprs)


def check(given, decide, constraints, rule, sense=None, target=None):
    """Return a list of (situation, model_result, rule_allows) failures."""
    gd, dd = domains(given), domains(decide)
    dnames = [n for n, _ in dd]
    failures = []
    for gvals in itertools.product(*(d for _, d in gd)):
        situation = dict(zip((n for n, _ in gd), gvals))
        feasible, wanted = [], []
        for dvals in itertools.product(*(d for _, d in dd)):
            env = {**situation, **dict(zip(dnames, dvals))}
            if holds(constraints, env):
                feasible.append(dvals)
            if holds([rule], env):
                wanted.append(dvals)
        got = feasible
        if sense and feasible:
            i = dnames.index(target)
            best = (max if sense == "max" else min)(v[i] for v in feasible)
            got = [v for v in feasible if v[i] == best]
        if not (set(got) <= set(wanted) and bool(got) == bool(wanted)):
            failures.append((situation, [dict(zip(dnames, v)) for v in got],
                             [dict(zip(dnames, v)) for v in wanted]))
    return failures


def selftest():
    AND = ["c <= a", "c <= b"]
    assert not check(["a", "b"], [], ["a <= b"], "(not a) or b"), "if-then"
    assert not check(["a", "b"], ["c"], AND + ["c >= a + b - 1"], "c == (a and b)"), "full AND"
    assert check(["a", "b"], ["c"], AND, "c == (a and b)"), "2-constraint AND must fail on its own"
    assert not check(["a", "b"], ["c"], AND, "c == (a and b)", "max", "c"), "2-constraint AND holds when maximising"
    assert check(["a", "b"], ["c"], AND, "c == (a and b)", "min", "c"), "2-constraint AND breaks when minimising"
    xy, zb = ["x=0..4", "y=0..4"], ["z=0..4", "b"]
    big_m = ["z <= x", "z <= y", "z >= x - (1 - b) * 4", "z >= y - b * 4"]
    assert not check(xy, zb, big_m, "z == min(x, y)"), "min with big-M, any direction"
    assert check(xy, ["z=0..4"], ["z <= x", "z <= y"], "z == min(x, y)", "min", "z"), "min without big-M breaks when minimising"
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--given", nargs="*", default=[])
    ap.add_argument("--decide", nargs="*", default=[])
    ap.add_argument("--constraint", action="append", default=[])
    ap.add_argument("--rule")
    ap.add_argument("--sense", choices=["max", "min"])
    ap.add_argument("--target")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.rule or (a.sense and a.target not in [n for n, _ in domains(a.decide)]):
        ap.error("--rule is required; --sense needs --target naming a --decide variable")
    failures = check(a.given, a.decide, a.constraint, a.rule, a.sense, a.target)
    if not failures:
        print("PASS: constraints match the rule in every situation")
        return
    label = "optimiser picks" if a.sense else "constraints allow"
    print(f"FAIL: {len(failures)} situation(s) disagree with the rule")
    for situation, got, wanted in failures:
        print(f"  situation {situation}: {label} {got or 'nothing (infeasible)'}; rule allows {wanted or 'nothing'}")
    sys.exit(1)


if __name__ == "__main__":
    main()
