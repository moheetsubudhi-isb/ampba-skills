#!/usr/bin/env python3
"""Run a data contract's quality checks against a CSV extract.

The contract is JSON. Every section is optional:

  {
    "row_count": {"min": 1000},
    "columns": {
      "order_id":   {"not_null": true, "unique": true},
      "status":     {"allowed": ["NEW", "SHIPPED", "DELIVERED"]},
      "amount":     {"not_null": true, "min": 0},
      "email":      {"pattern": "^[^@]+@[^@]+$"}
    },
    "unique_together": [["order_id", "line_no"]],
    "freshness": {"column": "updated_at", "max_age_hours": 26},
    "reconcile": {"column": "amount", "expected_sum": 125000.0, "tolerance": 0.001}
  }

Prints PASS or FAIL per check with the number of failing rows, and exits 1 if
any check fails, so a pipeline can block on it.

  python3 dq_contract_check.py --csv load.csv --contract contract.json [--now 2026-09-14T06:00:00]
  python3 dq_contract_check.py --selftest
Needs pandas.
"""
import argparse
import json
import sys

try:
    import pandas as pd
except ImportError:
    sys.exit("needs pandas: pip install pandas")


def run(df, contract, now):
    results = []

    def add(check, failing, detail=""):
        results.append((check, "PASS" if failing == 0 else "FAIL", int(failing), detail))

    if "row_count" in contract:
        lo = contract["row_count"].get("min", 0)
        add(f"row_count >= {lo}", int(len(df) < lo), f"{len(df)} rows")
    for col, rules in contract.get("columns", {}).items():
        if col not in df:
            add(f"{col} exists", 1, "column missing")
            continue
        s = df[col]
        if rules.get("not_null"):
            add(f"{col} not null", s.isna().sum())
        if rules.get("unique"):
            add(f"{col} unique", s.dropna().duplicated(keep=False).sum())
        if "allowed" in rules:
            bad = s.dropna()[~s.dropna().astype(str).isin([str(v) for v in rules["allowed"]])]
            add(f"{col} allowed values", len(bad), ", ".join(map(str, bad.unique()[:5])))
        num = pd.to_numeric(s, errors="coerce")
        if "min" in rules:
            add(f"{col} >= {rules['min']}", (num < rules["min"]).sum())
        if "max" in rules:
            add(f"{col} <= {rules['max']}", (num > rules["max"]).sum())
        if "pattern" in rules:
            add(f"{col} matches pattern", (~s.dropna().astype(str).str.match(rules["pattern"])).sum())
    for cols in contract.get("unique_together", []):
        add(f"unique {'+'.join(cols)}", df.duplicated(subset=cols, keep=False).sum())
    if "freshness" in contract:
        f = contract["freshness"]
        latest = pd.to_datetime(df[f["column"]], errors="coerce").max()
        age = (now - latest).total_seconds() / 3600
        add(f"freshness <= {f['max_age_hours']}h", int(age > f["max_age_hours"]), f"latest {latest}, {age:.1f}h old")
    if "reconcile" in contract:
        r = contract["reconcile"]
        total = pd.to_numeric(df[r["column"]], errors="coerce").sum()
        gap = abs(total - r["expected_sum"]) / max(abs(r["expected_sum"]), 1e-9)
        add(f"sum({r['column']}) reconciles", int(gap > r.get("tolerance", 0)),
            f"got {total:,.2f}, expected {r['expected_sum']:,.2f}, gap {gap:.2%}")
    return pd.DataFrame(results, columns=["check", "result", "failing", "detail"])


def selftest():
    df = pd.DataFrame({
        "order_id": [1, 2, 2, 4, 5],
        "status": ["NEW", "SHIPPED", "LOST", "NEW", None],
        "amount": [10.0, 20.0, -5.0, 30.0, 45.0],
        "updated_at": ["2026-09-13 20:00"] * 5,
    })
    contract = {
        "row_count": {"min": 3},
        "columns": {"order_id": {"not_null": True, "unique": True},
                    "status": {"not_null": True, "allowed": ["NEW", "SHIPPED"]},
                    "amount": {"min": 0}},
        "freshness": {"column": "updated_at", "max_age_hours": 6},
        "reconcile": {"column": "amount", "expected_sum": 100.0, "tolerance": 0.01},
    }
    out = run(df, contract, pd.Timestamp("2026-09-14 06:00")).set_index("check")
    assert out.loc["row_count >= 3", "result"] == "PASS"
    assert out.loc["order_id unique", "failing"] == 2, "both copies of a duplicate key are reported"
    assert out.loc["status allowed values", "detail"] == "LOST"
    assert out.loc["status not null", "failing"] == 1
    assert out.loc["amount >= 0", "failing"] == 1
    assert out.loc["freshness <= 6h", "result"] == "FAIL", "10 hours old breaks a 6-hour SLA"
    assert out.loc["sum(amount) reconciles", "result"] == "PASS", "a negative row can hide inside a matching total"
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--csv")
    ap.add_argument("--contract")
    ap.add_argument("--now", help="reference time for freshness; defaults to the current time")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not (a.csv and a.contract):
        ap.error("--csv and --contract are required")
    with open(a.contract) as fh:
        contract = json.load(fh)
    now = pd.Timestamp(a.now) if a.now else pd.Timestamp.now()
    out = run(pd.read_csv(a.csv), contract, now)
    print(out.to_string(index=False))
    failed = (out.result == "FAIL").sum()
    print(f"\n{len(out) - failed} passed, {failed} failed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
