# Statistics toolkit

Statistics skills for the moments that decide things at work: designing and reading A/B tests, comparing groups, estimating with a margin of error, setting control limits, checking causal claims, trusting a regression, giving honest prediction ranges, and modelling counts and rates.

Part of [Business Analytics Skills](https://github.com/moheetsubudhi-isb/business-analytics-skills), a set of agent skills that make an AI assistant work like a decision scientist and an advisor. Each skill asks what the work is for only when the answer would change the result, follows a real method step by step, runs a check wherever there is logic to verify, and hands back a plain-language brief plus a technical appendix.

## Skills (8)

- **causal-claim-check**: Pressure-test a claim that one thing caused another before anyone acts on it.
- **control-limits-and-error-costs**: Set the threshold for a monitored measurement or quality check, balancing false alarms against missed problems.
- **count-and-rate-models**: Model outcomes that are counts or rates, such as orders per day, defects per batch, claims per policy, visits per store or units sold per product and month.
- **estimate-with-margin-of-error**: Estimate a true average or rate from a sample and say how precise it is, or work out how big a sample is needed.
- **experiment-design-and-readout**: Design and read randomised experiments and A/B tests.
- **group-difference-test**: Check whether two groups, or two points in time, differ by more than chance in data you already have.
- **prediction-interval-reporting**: Give an honest range around a single prediction or forecast.
- **regression-diagnostics**: Read a regression output table and check whether it can be trusted for inference.

## Use

Skills load by themselves when a request matches. Ask a normal work question; to call one directly, type `/` and the skill name in Claude Code, Cursor or Copilot, or `$` and the name in Codex.

## What it runs

Instructions only, plus small optional Python checks (`scripts/`, standard library, numpy, pandas or scikit-learn) that read only the file you point them at. Nothing here reads credentials, environment secrets or your files on its own, makes network calls, or sends data anywhere.

## Licence

MIT. Source and issues: https://github.com/moheetsubudhi-isb/business-analytics-skills
