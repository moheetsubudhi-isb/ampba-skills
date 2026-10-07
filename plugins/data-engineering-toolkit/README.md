# Data engineering toolkit

Data-engineering skills for choosing where data should live, laying out distribution keys and partitions in MPP warehouses, and designing pipelines with data quality, reconciliation and governance built in.

Part of [Business Analytics Skills](https://github.com/moheetsubudhi-isb/business-analytics-skills), a set of agent skills that make an AI assistant work like a decision scientist and an advisor. Each skill asks what the work is for only when the answer would change the result, follows a real method step by step, runs a check wherever there is logic to verify, and hands back a plain-language brief plus a technical appendix.

## Skills (3)

- **datastore-selection**: Decide where data should live: a relational OLTP database, a columnar warehouse, a document store, a key-value cache, a graph database, a data lake or lakehouse, or a combination.
- **distribution-key-and-partitioning**: Choose how a large table is spread across nodes and split into partitions in an MPP warehouse or distributed store, and fix the skew and data movement that make queries slow.
- **pipeline-and-quality-design**: Design how data moves from source systems to its consumers, and how its quality is proven along the way.

## Use

Skills load by themselves when a request matches. Ask a normal work question; to call one directly, type `/` and the skill name in Claude Code, Cursor or Copilot, or `$` and the name in Codex.

## What it runs

Instructions only, plus small optional Python checks (`scripts/`, standard library, numpy, pandas or scikit-learn) that read only the file you point them at. Nothing here reads credentials, environment secrets or your files on its own, makes network calls, or sends data anywhere.

## Licence

MIT. Source and issues: https://github.com/moheetsubudhi-isb/business-analytics-skills
