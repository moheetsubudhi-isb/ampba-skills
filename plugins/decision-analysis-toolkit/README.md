# Decision analysis toolkit

Decision-analysis skills for structuring choices under uncertainty as decision trees, valuing information before paying for a test, survey or pilot, and designing Monte Carlo simulations for risk, inventory and schedule decisions.

Part of [Business Analytics Skills](https://github.com/moheetsubudhi-isb/business-analytics-skills), a set of agent skills that make an AI assistant work like a decision scientist and an advisor. Each skill asks what the work is for only when the answer would change the result, follows a real method step by step, runs a check wherever there is logic to verify, and hands back a plain-language brief plus a technical appendix.

## Skills (3)

- **decision-tree-analysis**: Decide between options whose payoff depends on uncertain outcomes, using a decision tree and expected monetary value (EMV).
- **simulation-model-design**: Design, run and read a Monte Carlo simulation when a plan depends on several uncertain inputs.
- **value-of-information**: Decide whether to buy information before a decision: a market test, pilot, survey, trial run, inspection, diagnostic, consultant report or extra data.

## Use

Skills load by themselves when a request matches. Ask a normal work question; to call one directly, type `/` and the skill name in Claude Code, Cursor or Copilot, or `$` and the name in Codex.

## What it runs

Instructions only, plus small optional Python checks (`scripts/`, standard library, numpy, pandas or scikit-learn) that read only the file you point them at. Nothing here reads credentials, environment secrets or your files on its own, makes network calls, or sends data anywhere.

## Licence

MIT. Source and issues: https://github.com/moheetsubudhi-isb/business-analytics-skills
