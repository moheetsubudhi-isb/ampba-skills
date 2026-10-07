# Pricing toolkit

Pricing and demand skills for estimating price and promotion elasticities, setting prices from willingness-to-pay research, and designing segment prices, tiers, bundles and product-line ladders.

Part of [Business Analytics Skills](https://github.com/moheetsubudhi-isb/business-analytics-skills), a set of agent skills that make an AI assistant work like a decision scientist and an advisor. Each skill asks what the work is for only when the answer would change the result, follows a real method step by step, runs a check wherever there is logic to verify, and hands back a plain-language brief plus a technical appendix.

## Skills (3)

- **price-elasticity-estimation**: Measure how sales respond to price and promotions, and turn the answer into a pricing call.
- **pricing-structure-design**: Design how prices differ across customers, versions and bundles so more value is captured without the low price leaking to everyone.
- **willingness-to-pay-research**: Set prices from what customers say or show they will pay: design the willingness-to-pay research, turn responses into demand at each price, and find the revenue- or profit-maximising price for each….

## Use

Skills load by themselves when a request matches. Ask a normal work question; to call one directly, type `/` and the skill name in Claude Code, Cursor or Copilot, or `$` and the name in Codex.

## What it runs

Instructions only, plus small optional Python checks (`scripts/`, standard library, numpy, pandas or scikit-learn) that read only the file you point them at. Nothing here reads credentials, environment secrets or your files on its own, makes network calls, or sends data anywhere.

## Licence

MIT. Source and issues: https://github.com/moheetsubudhi-isb/business-analytics-skills
