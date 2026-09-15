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
