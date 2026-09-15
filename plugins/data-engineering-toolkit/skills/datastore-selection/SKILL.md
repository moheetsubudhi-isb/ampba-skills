---
name: datastore-selection
description: >-
  Decide where data should live: a relational OLTP database, a columnar
  warehouse, a document store, a key-value cache, a graph database, a data
  lake or lakehouse, or a combination. Use whenever someone asks which
  database or storage to use for an application, feature or data product; SQL
  or NoSQL; Postgres vs MongoDB vs Cassandra vs Redis vs Neo4j vs ClickHouse vs
  BigQuery; data lake vs warehouse vs lakehouse or Delta Lake; OLTP vs OLAP;
  whether a system needs ACID transactions or can live with eventual
  consistency; how the CAP theorem applies; or how to design polyglot
  persistence for a platform with very different kinds of data. Also use to
  review a storage choice that is struggling with scale, latency or cost. Not
  for picking distribution or partition keys inside a chosen warehouse, and
  not for pipeline design or data quality rules.
---

# Datastore selection

Act as the data architect who places each kind of data in a store that fits how it is written and read, and as the advisor who keeps the number of systems as small as the requirements allow. Every extra database is another system to secure, back up, monitor and staff.

## Get the context that changes the answer

If a schema, sample records, query patterns or the current architecture are available, read them first.

Then ask only what that material cannot answer, and only if the answer would change the choice. Ask at most three questions. Give each one a one-line reason and a default. If the request is urgent, give a first recommendation on stated assumptions and list the questions that would sharpen it.

The questions that usually matter here:

1. **How is the data written and read?** Point lookups by key, transactions touching several rows, scans and aggregations over history, walks across relationships, or text search. Access patterns choose the store; data volume rarely does on its own.
2. **What happens if two users see different values for a few seconds, or a write is lost?** This decides between strict transactions and eventual consistency.
3. **What does the team already run well, and what are the volume and latency targets?** A store the team operates confidently beats a better fit nobody can support.

If there is no answer, assume money, stock and entitlements need strict consistency while feeds, counters and recommendations do not, and prefer the store the team already runs unless a stated requirement rules it out.

## Procedure

1. **List data domains and their access patterns.** One row each: domain · writes · reads · latency · consistency · size and growth. Choose per domain, not one store for everything.
2. **Map each domain to a store family**, then load the reference for each family in play.

   | Access pattern | Store family | Load |
   |---|---|---|
   | Transactions across related rows; strong integrity | Relational OLTP | `references/relational.md` |
   | Aggregations and scans over large history; BI | Columnar warehouse (OLAP) | `references/analytical-columnar.md` |
   | Flexible, nested records read whole by ID | Document store | `references/document.md` |
   | Very fast lookups by key; caches, sessions, counters, leaderboards | Key-value or in-memory | `references/key-value.md` |
   | Questions about relationships several hops deep | Graph database | `references/graph.md` |
   | Raw files of any shape, cheap history, ML, open formats | Data lake or lakehouse | `references/lake-and-lakehouse.md` |

3. **Check consistency against CAP.** When the network splits, a distributed store keeps either consistency or availability. Decide per domain which one it needs.
4. **Challenge every extra store.** Could the existing relational database cover it with JSON columns, a read replica, a materialised view or a text index? Add a store only when a named requirement fails in the one already running.
5. **Keep stores in step.** Give each domain one system of record. Feed other stores from it by change data capture or events, and state how stale each copy may be.
6. **Weigh cost and operations:** managed or self-hosted, backups, recovery time, security controls and the skills needed.

## Deliverable

**Part A: Architecture brief**, for the decision owner

- One table: domain · store · why · system of record · staleness allowed.
- How many systems that means, and what each costs to run.
- The main risk, and the trigger for revisiting the choice.

**Part B: Technical appendix**, for the engineers

- Access patterns and volumes per domain.
- Consistency analysis, sync design and migration path.
- Alternatives considered and the requirement each one failed.

## Traps

- Choosing NoSQL "for scale" when the data fits comfortably in one relational database.
- Using a warehouse as an application database with many small, concurrent writes.
- Running heavy analytics on the production transactional database.
- Treating a cache as the system of record.
- A graph database for data that is only one or two joins deep.
- A data lake with no catalog, schema or table format, which becomes a swamp.
- Two stores accepting writes for the same domain.
