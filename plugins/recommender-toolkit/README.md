# Recommender toolkit

Recommender-system skills for choosing and building association rules, collaborative filtering, matrix factorisation or graph ranking, and for evaluating recommenders offline and online with the right splits and ranking metrics.

Part of [Business Analytics Skills](https://github.com/moheetsubudhi-isb/business-analytics-skills), a set of agent skills that make an AI assistant work like a decision scientist and an advisor. Each skill asks what the work is for only when the answer would change the result, follows a real method step by step, runs a check wherever there is logic to verify, and hands back a plain-language brief plus a technical appendix.

## Skills (2)

- **recommender-build**: Build product, content or next-item recommendations, and choose the method that fits the data: association rules and market basket analysis, item-based or user-based collaborative filtering,….
- **recommender-evaluation**: Measure whether a recommender or ranking system is any good, offline and online.

## Use

Skills load by themselves when a request matches. Ask a normal work question; to call one directly, type `/` and the skill name in Claude Code, Cursor or Copilot, or `$` and the name in Codex.

## What it runs

Instructions only, plus small optional Python checks (`scripts/`, standard library, numpy, pandas or scikit-learn) that read only the file you point them at. Nothing here reads credentials, environment secrets or your files on its own, makes network calls, or sends data anywhere.

## Licence

MIT. Source and issues: https://github.com/moheetsubudhi-isb/business-analytics-skills
