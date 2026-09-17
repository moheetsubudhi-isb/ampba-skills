# distribution-key-and-partitioning

Use this skill when: Choose how a large table is spread across nodes and split into partitions in an MPP warehouse or distributed store, and fix the skew and data movement that make queries slow. Use whenever someone asks which distribution key, DISTKEY, DISTRIBUTED BY, hash distribution, sort key, partition key, shard key or clustering key to use; whether to hash, round-robin or replicate a table; why one node or partition is much bigger or slower than the rest; why joins shuffle or broadcast huge amounts of data; or how to partition a big fact table by date, region or tenant, in Redshift, Synapse, Greenplum, BigQuery, Snowflake, Databricks, Spark, Cassandra or similar. Also use when reviewing warehouse table DDL before it goes live. Not for choosing which kind of database to use, not for pipeline or data quality design, and not for reviewing or tuning Spark job code.

# Distribution key and partitioning

Act as the data engineer who lays out the table and as the advisor who explains what a bad layout costs. In a massively parallel warehouse, where a row lives decides how much work each node does and how much data crosses the network on every join.

## Get the context that changes the answer

If DDL, a query plan, table sizes or a sample of key values are available, read them first: row counts, the cardinality of candidate keys, the share of NULLs, and the joins and filters in the heaviest queries.

Then ask only what that material cannot answer, and only if the answer would change the layout. Ask at most three questions. Give each one a one-line reason and a default. If the request is urgent, give a first layout on stated assumptions and list the questions that would sharpen it.

The questions that usually matter here:

1. **Which queries matter most, and what do they join and filter on?** The key follows the workload, not the table.
2. **How big are the tables, and how fast do they grow?** Small tables are usually cheaper to copy to every node than to distribute.
3. **Which platform is it?** Redshift, Synapse and Greenplum take an explicit distribution key. BigQuery and Snowflake distribute rows themselves, so the levers there are partitioning and clustering.

If there is no answer, assume an explicit-key warehouse: hash-distribute large fact tables on their most common join key, replicate small dimension tables, and partition facts by event date.

## Procedure

Where a step names a script and code cannot run here, do the same check by hand on a small case, and say in the deliverable that it was done by hand.

1. **Classify each table** as large fact, large dimension, small dimension or staging, with row counts and growth.
2. **Pick the distribution style.**

   | Table | Style | Why |
   |---|---|---|
   | Small dimension joined often | Replicate (ALL) | Every node has a copy, so joins to it move no data |
   | Large fact or large dimension | Hash on a key | Rows with the same key land on the same node |
   | Staging, or no dominant join | Round-robin (EVEN) | Fast loads and an even spread; joins will move data |

3. **Choose the hash key.** A good key passes all four tests:
   - **High cardinality:** many distinct values.
   - **Even:** no single value holds a large share of the rows.
   - **Few NULLs:** every NULL hashes to the same node.
   - **Used in joins:** ideally the same key on both sides of the biggest join, so the join runs locally on each node.

   When the best join key fails the evenness test, prefer evenness and accept data movement on that join. A skewed node slows every query that touches the table.
4. **Measure skew before committing.** Run `scripts/skew_check.py` on a sample of each candidate column. It hashes the values across the node count and reports rows per node, the max-to-mean ratio, the NULL share and the largest values. A ratio under 1.2 is healthy; above 2 needs a different key.
5. **Partition separately from distribution.** Distribution spreads rows across nodes; partitioning splits a table so queries can skip data. Partition on the column most queries filter by range, usually event date. Avoid thousands of tiny partitions. Use sort or clustering keys to order rows within partitions for range scans.
6. **Operational stores** (Cassandra, MongoDB, DynamoDB): the shard or partition key must spread writes and serve the main lookup. Keys that always increase, such as timestamps or sequence IDs, send every new write to one shard; add a hash or bucket prefix.
7. **Verify on the real workload.** Compare query plans before and after, looking for redistribute, broadcast or shuffle steps on the heaviest joins, and check rows per node in the system tables.

## Deliverable

**Part A: Layout brief**, for the decision owner

- One table: table · distribution style · key · partitioning · sort or clustering key.
- The expected effect on the heaviest queries, in plain terms.
- The single biggest risk, such as one tenant growing until its key skews, and what to monitor.

**Part B: Technical appendix**, for the engineers

- DDL for the platform in use.
- The skew check output for each candidate key.
- Query-plan evidence, and the rebuild plan: redistribution rewrites the table, so state the order, the free space needed and how to roll back.

## Traps

- Distributing on a low-cardinality column such as status, country or a flag.
- Distributing on a nullable foreign key, so all the NULLs pile onto one node.
- Choosing the primary key only because it is unique, when no query joins on it.
- Distributing on a column used mainly in filters, which sends each filtered query to one node.
- Replicating a dimension table that later grows large.
- Partitioning by hour on a table too small to need it.
- Checking skew on one day's sample when a large customer arrives next quarter.
