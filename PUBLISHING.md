# Publishing checklist

Run before every release. All of it is automated except the portal steps.

1. `python3 tools/validate_skills.py` and `python3 tools/build_marketplaces.py --check` and `python3 tools/build_bundles.py --check` all pass (CI runs them).
2. `claude plugin validate .` passes for the root and for each `plugins/<toolkit>`.
3. Each toolkit folder holds `README.md` (40+ words), `.claude-plugin/plugin.json` with `license`, and `.claude-plugin/icon.png` (square, 512 to 2048 px).
4. No `eval`, `exec`, `subprocess` or environment reads in any script (the directory scan holds on them).

## Claude

- Claude Code: `/plugin marketplace add moheetsubudhi-isb/business-analytics-skills`, then `/plugin install <toolkit>@business-analytics-skills`.
- Anthropic directory: claude.ai/directory/manage, one submission per `plugins/<toolkit>` folder (7 in all). Limit 10 per 24 hours.
- claude.ai chat: upload `dist/<skill>.zip` under Customize, Skills.

## ChatGPT and Codex

- Codex: `codex plugin marketplace add moheetsubudhi-isb/business-analytics-skills`.
- ChatGPT: upload `dist/<skill>.zip` where Skills upload is on the plan; otherwise paste `dist/text/<skill>.md` into a Project.
