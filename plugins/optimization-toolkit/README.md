# Optimization toolkit

Decision-science skills for turning business decisions into optimisation models, writing business rules correctly, allocating scarce supply fairly, choosing exact solvers or heuristics, and testing models before go-live.

Part of [Business Analytics Skills](https://github.com/moheetsubudhi-isb/business-analytics-skills), a set of agent skills that make an AI assistant work like a decision scientist and an advisor. Each skill asks what the work is for only when the answer would change the result, follows a real method step by step, runs a check wherever there is logic to verify, and hands back a plain-language brief plus a technical appendix.

## Skills (5)

- **exact-vs-heuristic**: Choose between an exact solver and a heuristic for a hard planning problem, and set honest expectations on speed, plan quality and explainability.
- **logical-constraints**: Write yes/no business rules as correct linear constraints in a mixed-integer model, then prove them right by enumeration.
- **optimization-formulation**: Turn a business decision into an optimisation model and a recommendation a business owner can act on.
- **or-model-test-plan**: Plan how to test an optimisation model so its plans can be trusted in live operations.
- **shortage-allocation-fairness**: Decide who gets what when there is not enough to go round, and explain the trade-off between efficiency and fairness to the people affected.

## Use

Skills load by themselves when a request matches. Ask a normal work question; to call one directly, type `/` and the skill name in Claude Code, Cursor or Copilot, or `$` and the name in Codex.

## What it runs

Instructions only, plus small optional Python checks (`scripts/`, standard library, numpy, pandas or scikit-learn) that read only the file you point them at. Nothing here reads credentials, environment secrets or your files on its own, makes network calls, or sends data anywhere.

## Licence

MIT. Source and issues: https://github.com/moheetsubudhi-isb/business-analytics-skills
