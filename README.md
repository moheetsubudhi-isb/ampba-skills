# AMPBA Skills

Skills that make an AI assistant work like a decision scientist and an advisor, not just a calculator. Each skill:

- asks what the work is for, but only when the answer would change the result;
- follows a real method, step by step;
- runs a check wherever there is logic to verify;
- hands back a plain-language decision brief for the decision owner, plus a technical appendix for the people who build it.

The methods come from analytics coursework at ISB (AMPBA), rewritten from scratch for everyday work. The repository contains no course slides, cases, datasets or faculty material, and every example is invented.

## Toolkits

| Toolkit | Skills | Status |
|---|---|---|
| `optimization-toolkit` | `optimization-formulation`, `logical-constraints`, `shortage-allocation-fairness`, `exact-vs-heuristic`, `or-model-test-plan` | Pilot |

See [catalog.md](catalog.md) for the moment each skill handles.

## Install

**Claude Code**
```
/plugin marketplace add moheetsubudhi-isb/ampba-skills
/plugin install optimization-toolkit@ampba-skills
```

**Codex and ChatGPT.** Skills use the shared `SKILL.md` format. Copy a skill folder, such as `plugins/optimization-toolkit/skills/logical-constraints`, into `~/.agents/skills/` to use it everywhere, or into `.agents/skills/` inside one project. See OpenAI's [Build skills guide](https://learn.chatgpt.com/docs/build-skills) for ChatGPT.

**Any other assistant.** Paste the contents of `SKILL.md` into its instructions.

Scripts need only Python 3 and its standard library.

## Academic integrity

These skills are for work and learning. Don't use them for graded coursework wherever your course restricts AI-assisted work.

## Contributing

- Run `python tools/validate_skills.py` and every script's `--selftest` before committing. CI runs both, along with a secret scan.
- Keep frontmatter to `name` and `description` so skills stay portable.
- Encode the method, not the course material. Invent examples.
