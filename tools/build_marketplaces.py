#!/usr/bin/env python3
"""Generate every harness's plugin manifests from one source.

The source of truth is .claude-plugin/marketplace.json: it names each toolkit,
where it lives and what it is for. Everything else here is derived, so the two
marketplaces can never disagree about what this repo ships.

  python3 tools/build_marketplaces.py           write the generated files
  python3 tools/build_marketplaces.py --check   fail if they are out of date (CI)

Generated:
  .agents/plugins/marketplace.json            Codex / ChatGPT: codex plugin marketplace add
  plugins/<toolkit>/plugin.json               portable Agent Plugins manifest (Codex)
  plugins/<toolkit>/.claude-plugin/plugin.json  same facts where Claude Code looks for them
  plugins/<toolkit>/README.md                 what the plugin directory shows as the listing

Claude Code reads only the .claude-plugin/ copy. Without it, it invents a
manifest and stamps every toolkit 0.1.0, dropping the licence and homepage.
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SOURCE = ROOT / ".claude-plugin" / "marketplace.json"

REPO_URL = "https://github.com/moheetsubudhi-isb/business-analytics-skills"
GIT_URL = REPO_URL + ".git"
REF = "main"
VERSION = "1.0.0"
AUTHOR = "Moheet Subudhi"
CATEGORY = "Productivity"
PLUGIN_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"


def display_name(slug):
    return slug.replace("-", " ").capitalize()


def short(description, limit=120):
    """First sentence, clipped, for the one-line slot in a plugin directory."""
    first = description.split(". ")[0].rstrip(".")
    if len(first) <= limit:
        return first
    return first[:limit].rsplit(" ", 1)[0] + "…"


def skill_summaries(plugin_dir):
    """[(name, first sentence)] for every skill folder, read from SKILL.md front matter."""
    rows = []
    for md in sorted((ROOT / plugin_dir / "skills").glob("*/SKILL.md")):
        head = re.match(r"^---\n(.*?)\n---\n", md.read_text(), re.S).group(1)
        body = re.search(r"description: >-\n((?:  .*\n?)+)", head + "\n").group(1)
        text = " ".join(line.strip() for line in body.splitlines())
        rows.append((md.parent.name, short(text, 200)))
    return rows


def readme(name, desc, plugin_dir):
    skills = skill_summaries(plugin_dir)
    lines = [f"# {display_name(name)}", "", desc, "",
             "Part of [Business Analytics Skills](" + REPO_URL + "), a set of agent skills that make an AI "
             "assistant work like a decision scientist and an advisor. Each skill asks what the work is for "
             "only when the answer would change the result, follows a real method step by step, runs a check "
             "wherever there is logic to verify, and hands back a plain-language brief plus a technical "
             "appendix.", "", f"## Skills ({len(skills)})", ""]
    lines += [f"- **{n}**: {s}." for n, s in skills]
    lines += ["", "## Use", "",
              "Skills load by themselves when a request matches. Ask a normal work question; to call one "
              "directly, type `/` and the skill name in Claude Code, Cursor or Copilot, or `$` and the name in Codex.", "",
              "## What it runs", "",
              "Instructions only, plus small optional Python checks (`scripts/`, standard library, numpy, pandas "
              "or scikit-learn) that read only the file you point them at. Nothing here reads credentials, "
              "environment secrets or your files on its own, makes network calls, or sends data anywhere.", "",
              "## Licence", "", f"MIT. Source and issues: {REPO_URL}", ""]
    return "\n".join(lines)


def generated(source):
    """Return {path: text} for every file this script owns."""
    out = {}
    entries = []
    for plugin in source["plugins"]:
        name, desc = plugin["name"], plugin["description"]
        path = plugin["source"].lstrip("./")

        # Claude Code's location. Keys limited to the ones it reads.
        out[f"{path}/.claude-plugin/plugin.json"] = json.dumps({
            "name": name,
            "version": VERSION,
            "description": desc,
            "author": {"name": AUTHOR},
            "homepage": REPO_URL,
            "repository": REPO_URL,
            "license": "MIT",
            "keywords": ["analytics", "decision-support", name.replace("-toolkit", "")],
        }, indent=2) + "\n"

        out[f"{path}/README.md"] = readme(name, desc, path)

        # Portable Agent Plugins location, which Codex reads.
        out[f"{path}/plugin.json"] = json.dumps({
            "$schema": PLUGIN_SCHEMA,
            "name": name,
            "version": VERSION,
            "description": desc,
            "author": {"name": AUTHOR},
            "homepage": REPO_URL,
            "repository": REPO_URL,
            "license": "MIT",
            "keywords": ["analytics", "decision-support", name.replace("-toolkit", "")],
            "extensions": {
                "com.openai": {
                    "interface": {
                        "displayName": display_name(name),
                        "shortDescription": short(desc),
                        "longDescription": desc,
                        "developerName": AUTHOR,
                        "category": CATEGORY,
                    }
                }
            },
        }, indent=2) + "\n"

        entries.append({
            "name": name,
            "description": desc,
            "source": {
                "source": "git-subdir",
                "url": GIT_URL,
                "path": f"./{path}",
                "ref": REF,
            },
            "policy": {"installation": "AVAILABLE"},
            "category": CATEGORY,
        })

    out[".agents/plugins/marketplace.json"] = json.dumps({
        "name": source["name"],
        "interface": {"displayName": "Business Analytics Skills"},
        "plugins": entries,
    }, indent=2) + "\n"
    return out


def main():
    check = "--check" in sys.argv
    files = generated(json.loads(SOURCE.read_text()))
    stale = []
    for rel, text in sorted(files.items()):
        p = ROOT / rel
        if p.exists() and p.read_text() == text:
            continue
        stale.append(rel)
        if not check:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text)
    if check:
        for rel in stale:
            print("FAIL out of date:", rel)
        print(f"{len(files)} manifests checked, {len(stale)} out of date")
        sys.exit(1 if stale else 0)
    print(f"wrote {len(files)} manifests ({len(stale)} changed)")


if __name__ == "__main__":
    main()
