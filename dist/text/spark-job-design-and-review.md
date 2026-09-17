# spark-job-design-and-review

Use this skill when: Write, review and speed up Apache Spark jobs in PySpark, Scala or Spark SQL, including on Databricks, EMR or Dataproc. Use whenever someone asks why a Spark job is slow, runs out of memory or has one straggling task; how to read the Spark UI, stages and shuffles; RDD vs DataFrame vs Spark SQL; transformations vs actions and lazy evaluation; narrow vs wide transformations; groupByKey vs reduceByKey; when to cache or persist; how many partitions to use, repartition vs coalesce; broadcast joins and join skew or salting; why collect() or toPandas() crashes the driver; UDFs vs built-in functions; writing too many small files; or wants a code review of a Spark notebook or job before it goes to production. Not for choosing distribution or partition keys for warehouse tables, not for choosing a database, and not for sizing HDFS storage or cluster nodes.

# Spark job design and review

Act as the senior data engineer who reviews Spark code before it reaches production, and as the advisor who explains the fix in terms of time and cost. Most slow Spark jobs have the same few causes: needless shuffles, data pulled to the driver, skew, and too many or too few partitions.

## Get the context that changes the answer

If code, a notebook, a query plan (`explain()`) or Spark UI screenshots are available, look at them first: the actions called, the joins and aggregations, the stage with the longest time or biggest shuffle, and task time spread within that stage.

Then ask only what that material cannot answer, and only if the answer would change the fix. Ask at most three questions. Give each one a one-line reason and a default. If the request is urgent, give the likely fixes on stated assumptions and list the questions that would sharpen them.

The questions that usually matter here:

1. **How big are the inputs, and how big is the smaller side of each join?** This decides broadcast vs shuffle joins.
2. **What is the symptom?** Slow overall, one straggling task, driver out of memory, or executor out of memory; each points to a different cause.
3. **Is this batch or streaming, and how often does it run?** A one-off backfill and a job every 15 minutes justify different effort.

If there is no answer, assume a batch job on a DataFrame API, inputs in columnar files, and default cluster settings with adaptive query execution on.

## Procedure

Where a step names a script and code cannot run here, do the same check by hand on a small case, and say in the deliverable that it was done by hand.

1. **Scan the code** for known anti-patterns with `scripts/spark_lint.py path/to/job.py`. It flags `collect()` and `toPandas()` on large frames, `groupByKey`, Python UDFs where a built-in exists, actions inside loops, frames reused without caching, `repartition(1)`, and writes with no partition control. Treat its output as leads to confirm, not verdicts.
2. **Prefer DataFrames and Spark SQL over RDDs.** The optimiser (Catalyst) can prune columns, push filters to the source and choose join strategies only for DataFrame and SQL code. Keep Python UDFs out of hot paths; use built-in functions or pandas UDFs.
3. **Know where the shuffles are.** Narrow transformations (`select`, `filter`, `withColumn`, `map`) stay in one partition. Wide ones (`groupBy`, `join`, `distinct`, `orderBy`, `repartition`) shuffle data across the network and start a new stage. Filter and select before the first wide step. Use `reduceByKey` or DataFrame aggregations, which combine locally before shuffling; `groupByKey` ships every row.
4. **Remember laziness.** Transformations only build a plan; each action (`count`, `show`, `collect`, `write`) runs the whole lineage again. Cache or persist a frame only when two or more actions reuse it, and unpersist when done. A `count()` just to log a number doubles the work.
5. **Keep data off the driver.** `collect()` and `toPandas()` bring every row to one machine. Aggregate or `limit` first, or write results out.
6. **Fix joins.** Broadcast the small side (below a few hundred MB) with `broadcast()` or let adaptive execution do it. For a skewed key, check key counts, enable skew-join handling, or salt the hot key.
7. **Size partitions.** Aim for roughly 100 to 200 MB per partition. `repartition(n)` does a full shuffle and can raise the count; `coalesce(n)` only merges and is cheap for reducing. Set `spark.sql.shuffle.partitions` to the data, or let adaptive execution coalesce. Before writing, control file count so the output is not thousands of tiny files.
8. **Read the Spark UI** to confirm: the slowest stage, shuffle read and write sizes, the max vs median task time (a big gap means skew), spill to disk, and garbage-collection time.
9. **Measure before and after** on the same input and cluster, and report both run time and cost.

## Deliverable

**Part A: Review summary**, for the job owner

- The two or three changes that matter most, each with its expected effect on run time, cost or reliability.
- Risks: anything that could change results, not just speed.
- The measured or expected before-and-after.

**Part B: Engineering appendix**, for the engineers

- Line-by-line findings with the suggested code change.
- Evidence from the query plan or Spark UI.
- Configuration changes, and how they were tested.

## Traps

- Calling `collect()` or `toPandas()` on a large DataFrame.
- Caching everything, which fills executor memory and slows the job.
- `groupByKey` where an aggregation that combines locally would do.
- Python UDFs for logic a built-in function already provides.
- `repartition(1)` to get one output file from a large dataset.
- Tuning memory settings before removing an unneeded shuffle.
- Fixing a skewed join by adding executors.
- Comparing run times on different input sizes or cluster states.
