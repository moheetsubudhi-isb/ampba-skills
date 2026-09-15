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
