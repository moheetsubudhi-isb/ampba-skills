#!/usr/bin/env python3
"""Validate every SKILL.md in the repo.

Limits mirror Anthropic's skill-creator quick_validate.py. Frontmatter is
restricted to name + description so the same folder loads in Claude Code,
Codex and ChatGPT without edits.

  python tools/validate_skills.py
"""
import pathlib
import re
import sys

import yaml

PORTABLE_KEYS = {"name", "description"}
NAME_RE = re.compile(r"[a-z0-9]+(-[a-z0-9]+)*")

root = pathlib.Path(__file__).resolve().parent.parent
paths = sorted(root.glob("plugins/*/skills/*/SKILL.md"))
errors = [] if paths else ["no SKILL.md files found under plugins/*/skills/"]

for p in paths:
    rel = p.relative_to(root)
    m = re.match(r"^---\n(.*?)\n---\n", p.read_text(), re.S)
    if not m:
        errors.append(f"{rel}: missing YAML frontmatter")
        continue
    try:
        fm = yaml.safe_load(m.group(1))
    except yaml.YAMLError as e:
        errors.append(f"{rel}: invalid YAML: {e}")
        continue
    if not isinstance(fm, dict):
        errors.append(f"{rel}: frontmatter must be a mapping")
        continue
    extra = set(fm) - PORTABLE_KEYS
    if extra:
        errors.append(f"{rel}: non-portable keys {sorted(extra)}; keep only name and description")
    name, desc = fm.get("name"), fm.get("description")
    if not isinstance(name, str) or not NAME_RE.fullmatch(name) or len(name) > 64:
        errors.append(f"{rel}: name must be kebab-case, at most 64 characters")
    elif name != p.parent.name:
        errors.append(f"{rel}: name '{name}' must match folder '{p.parent.name}'")
    if not isinstance(desc, str) or not desc.strip():
        errors.append(f"{rel}: description is required")
    elif len(desc) > 1024:
        errors.append(f"{rel}: description is {len(desc)} characters; maximum is 1024")
    elif "<" in desc or ">" in desc:
        errors.append(f"{rel}: description must not contain angle brackets")

for e in errors:
    print("FAIL", e)
print(f"{len(paths)} skills checked, {len(errors)} problems")
sys.exit(1 if errors else 0)
