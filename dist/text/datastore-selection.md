# datastore-selection

Use this skill when: Decide where data should live: a relational OLTP database, a columnar warehouse, a document store, a key-value cache, a graph database, a data lake or lakehouse, or a combination. Use whenever someone asks which database or storage to use for an application, feature or data product; SQL or NoSQL; Postgres vs MongoDB vs Cassandra vs Redis vs Neo4j vs ClickHouse vs BigQuery; data lake vs warehouse vs lakehouse or Delta Lake; OLTP vs OLAP; whether a system needs ACID transactions or can live with eventual consistency; how the CAP theorem applies; or how to design polyglot persistence for a platform with very different kinds of data. Also use to review a storage choice that is struggling with scale, latency or cost. Not for picking distribution or partition keys inside a chosen warehouse, and not for pipeline design or data quality rules.

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

---

## Reference: references/analytical-columnar.md

# Columnar warehouses and OLAP stores

**Use when** people aggregate, filter and scan large volumes of history: BI dashboards, finance reporting, time series, log and event analytics.

**Examples:** BigQuery, Snowflake, Redshift, Synapse, ClickHouse, Druid, DuckDB for local work.

**Strengths**
- Stores each column separately, so a query reads only the columns it needs.
- Similar values sit together and compress well, cutting storage and I/O.
- Parallel scans across nodes make SUM, AVG and COUNT over billions of rows fast.
- ClickHouse and Druid serve near-real-time analytics on streaming data.

**Limits**
- Poor at many small, concurrent updates or single-row lookups; not an application database.
- Updates and deletes are costly or batch-oriented in many engines.
- Costs follow data scanned or compute time; unbounded queries get expensive.

**Design notes**
- Model for reading: star schemas with fact and dimension tables, or wide denormalised tables.
- Partition and cluster on the columns queries filter by; in explicit-key engines, choose distribution keys carefully (see the distribution-key-and-partitioning skill).
- Load in batches or micro-batches rather than row by row.

---

## Reference: references/document.md

# Document stores

**Use when** records vary in shape, nest naturally, and are usually read or written whole by ID: product catalogues with category-specific attributes, user profiles, content, configuration.

**Examples:** MongoDB, Couchbase, Firestore, Cosmos DB.

**Strengths**
- Flexible schema: two products in one collection can carry different fields.
- Nested objects and arrays map directly to application objects, avoiding many joins.
- Scales out by sharding on a document key.
- Rich queries, secondary indexes and aggregation pipelines.

**Limits**
- Relationships across documents are weaker than foreign keys; integrity moves into application code.
- Transactions across many documents exist but cost more than in relational databases.
- "Schema-less" still needs a schema in practice; without validation, fields drift.

**Design notes**
- Model around the main read: embed what is read together, reference what changes independently or grows without bound.
- Turn on schema validation for required fields and types.
- Choose the shard key for even writes and the main lookup; avoid always-increasing keys.

---

## Reference: references/graph.md

# Graph databases

**Use when** the questions are about relationships several hops deep, and the relationships matter as much as the records: fraud rings, social connections, recommendations from shared behaviour, network and IT dependencies, supply chains, master data linking, knowledge graphs.

**Examples:** Neo4j, Amazon Neptune, TigerGraph, Memgraph.

**Structure:** nodes are entities, edges are relationships, and both carry properties.

**Strengths**
- Traversals such as "accounts sharing a device with an account that shared a card with a flagged account" stay fast as depth grows, where SQL needs many self-joins.
- Path, centrality and community algorithms run close to the data.
- The model reads like the business domain.

**Limits**
- Poor at large aggregations and bulk scans; pair with a warehouse for reporting.
- Fewer people know the query languages (Cypher, Gremlin, SPARQL).
- Scaling a single very large graph across machines is harder than scaling rows.

**Design notes**
- Confirm the need: if questions rarely go beyond two joins, a relational database is simpler.
- Model the questions first, then the nodes and edges that answer them.
- Keep the graph fed from a system of record rather than writing to it directly from many services.

---

## Reference: references/key-value.md

# Key-value and in-memory stores

**Use when** the application reads and writes by a known key and needs very low latency: caches, sessions, rate limits, counters, leaderboards, feature lookups at serving time, shopping carts.

**Examples:** Redis, Memcached, DynamoDB, etcd.

**Strengths**
- Simple model: get and put by key, often in under a millisecond.
- Scales out by spreading keys across nodes.
- Redis adds sorted sets for rankings, pub/sub, streams, TTL expiry and geospatial indexes.

**Limits**
- No ad-hoc queries by value; access paths must be known in advance.
- In-memory stores are bounded by RAM and lose data on failure unless persistence is on (snapshots or append-only logs) and replicas are configured.
- A cache that falls out of step with its source serves stale data.

**Design notes**
- Keep the system of record elsewhere; treat a cache as disposable and rebuildable.
- Set expiry times and an invalidation rule for every cached key.
- Plan for a cold cache after restarts so the source database is not overwhelmed.

---

## Reference: references/lake-and-lakehouse.md

# Data lakes and lakehouses

**Use when** many sources of structured, semi-structured and unstructured data must be kept cheaply in their original form, for history, replay, machine learning and later analysis.

**Examples:** object storage (S3, ADLS, GCS) with open table formats (Delta Lake, Apache Iceberg, Apache Hudi), queried by Spark, Databricks, Trino, Snowflake or BigQuery.

**Lake vs lakehouse**
- A plain lake is files in folders. Cheap and flexible, but no transactions, weak schema control and slow discovery.
- A lakehouse adds a table format on top: ACID transactions, schema enforcement and evolution, time travel, and faster queries through file statistics and data layout. It serves BI and ML from one copy.
- A warehouse remains simpler when all data is structured and the main use is SQL reporting.

**Medallion layout**
- **Bronze:** raw data as landed, immutable, with load metadata. Allows replay.
- **Silver:** cleaned, deduplicated, typed, with conformed keys.
- **Gold:** business-level aggregates and data products for dashboards and models.

**Limits**
- Without a catalog, owners and schemas, a lake turns into a swamp nobody trusts.
- Many small files slow queries; compact them on a schedule.
- Access control and PII handling need deliberate design across layers.

**Design notes**
- Use an open table format from day one rather than raw files.
- Register every table in a catalog with an owner and a description.
- Partition by the column most reads filter on, usually date, and keep file sizes reasonable.

---

## Reference: references/relational.md

# Relational OLTP databases

**Use when** the data has clear relationships, many small transactions update several rows together, and integrity matters: orders, payments, inventory, accounts, entitlements.

**Examples:** PostgreSQL, MySQL, SQL Server, Oracle; distributed SQL such as CockroachDB, Spanner or YugabyteDB when one node is not enough.

**Strengths**
- ACID transactions: atomic, consistent, isolated, durable. A transfer either happens completely or not at all.
- Constraints enforce integrity: primary keys, foreign keys, unique and check constraints.
- One well-understood query language, mature tooling, backups and replication.
- JSON columns, full-text indexes and read replicas cover many needs that tempt teams toward extra stores.

**Limits**
- Scales up easily; scaling writes out across many nodes needs sharding or distributed SQL.
- Row storage makes large scans and aggregations slow; send analytics to a warehouse or replica.
- Schema changes on very large tables need planning.

**Design notes**
- Normalise for writes; denormalise only for proven read paths.
- Index for the real queries, and check plans before adding hardware.
- Keep reporting off the primary: use a read replica or feed a warehouse.
