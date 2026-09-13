#!/usr/bin/env python3
"""Measure whether a skill triggers on queries it should, and stays quiet otherwise.

Installs the skill under .claude/skills/ for the run, then scans the whole
transcript of each `claude -p` run for a Skill or Read call naming it. Scanning
the whole transcript matters: a CLAUDE.md that makes Claude call another tool
first does not mean the skill was skipped.

  python3 tools/trigger_eval.py --skill plugins/*/skills/logical-constraints \
      --eval-set evals/logical-constraints.json --runs 1
"""
import argparse
import json
import os
import pathlib
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

ROOT = pathlib.Path(__file__).resolve().parent.parent


def triggered(query, name, model, timeout):
    cmd = ["claude", "-p", query, "--output-format", "stream-json", "--verbose"]
    if model:
        cmd += ["--model", model]
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    try:
        out = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True,
                             text=True, timeout=timeout).stdout
    except subprocess.TimeoutExpired:
        return None
    for line in out.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") != "assistant":
            continue
        for c in event.get("message", {}).get("content", []):
            if c.get("type") != "tool_use":
                continue
            arg = str(c.get("input", {}))
            if c.get("name") in ("Skill", "Read") and name in arg:
                return True
    return False


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--skill", required=True)
    ap.add_argument("--eval-set", required=True)
    ap.add_argument("--runs", type=int, default=1)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--timeout", type=int, default=180)
    ap.add_argument("--model")
    a = ap.parse_args()

    skill = pathlib.Path(a.skill).resolve()
    name = skill.name
    installed = ROOT / ".claude" / "skills" / name
    installed.parent.mkdir(parents=True, exist_ok=True)
    if installed.exists() or installed.is_symlink():
        shutil.rmtree(installed, ignore_errors=True)
        installed.unlink(missing_ok=True)
    installed.symlink_to(skill)
    try:
        rows = json.loads(pathlib.Path(a.eval_set).read_text())
        jobs = [(r, i) for r in rows for i in range(a.runs)]
        with ThreadPoolExecutor(max_workers=a.workers) as pool:
            hits = list(pool.map(lambda j: triggered(j[0]["query"], name, a.model, a.timeout), jobs))
        results, errors = [], hits.count(None)
        for i, row in enumerate(rows):
            runs = [h for h in hits[i * a.runs:(i + 1) * a.runs] if h is not None]
            rate = sum(runs) / len(runs) if runs else None
            # every run timed out: unknown, not a failure
            verdict = None if rate is None else (rate >= 0.5) == row["should_trigger"]
            results.append({**row, "trigger_rate": rate, "runs_ok": len(runs), "pass": verdict})
        passed = sum(r["pass"] is True for r in results)
        unknown = sum(r["pass"] is None for r in results)
        print(json.dumps({"skill": name, "passed": passed, "unknown": unknown,
                          "total": len(results), "timed_out_runs": errors,
                          "results": results}, indent=1))
        for r in results:
            if r["pass"] is None:
                print(f"  UNKNOWN (all runs timed out): {r['query'][:70]}", file=sys.stderr)
            elif not r["pass"]:
                print(f"  MISS rate={r['trigger_rate']:.2f} expected={r['should_trigger']}: {r['query'][:70]}", file=sys.stderr)
        sys.exit(0 if passed == len(results) else 1)
    finally:
        installed.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
