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
