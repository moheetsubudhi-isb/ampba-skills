# cluster-storage-and-sizing

Use this skill when: Size and lay out storage for a Hadoop-style distributed file system (HDFS) or a self-managed big-data cluster, and decide when object storage should replace it. Use whenever someone asks how many nodes or how much raw disk a cluster needs for a given volume of data; how block size and replication factor affect capacity and reliability; why the NameNode is short of memory or why millions of small files hurt; how rack awareness, data locality and node failure work; how to compact small files; whether to keep HDFS or move to S3, ADLS or GCS with compute separated from storage; or how YARN, the NameNode and DataNodes fit together. Not for choosing between database types or lake vs warehouse, not for warehouse distribution or partition keys, and not for tuning Spark job code.

# Cluster storage and sizing

Act as the platform engineer who sizes the cluster, and as the advisor who says when a cluster is the wrong answer. Capacity planning is arithmetic; the judgement is in the replication, growth and file-size assumptions behind it.

## Get the context that changes the answer

If an inventory of current data, a cluster configuration or growth figures are available, look at them first: data volume today, daily ingest, file counts and average file size, retention, and replication settings.

Then ask only what that material cannot answer, and only if the answer would change the sizing or the platform choice. Ask at most three questions. Give each one a one-line reason and a default. If the request is urgent, give a first sizing on stated assumptions and list the questions that would sharpen it.

The questions that usually matter here:

1. **How much data today, how fast does it grow, and how long is it kept?** Retention often matters more than today's size.
2. **How many files, and how small are they?** File count drives NameNode memory, not bytes.
3. **Is the cluster on premises or in the cloud, and must compute run all the time?** Idle clusters in the cloud usually cost more than object storage with on-demand compute.

If there is no answer, assume replication factor 3, 128 MB blocks, 25% free-space headroom, compression of 3× for columnar files, and 3 years of growth.

## Procedure

Where a step names a script and code cannot run here, do the same check by hand on a small case, and say in the deliverable that it was done by hand.

1. **Know the moving parts.** The NameNode holds all file and block metadata in memory; DataNodes store blocks; each block is replicated (default 3) across nodes and racks. YARN schedules compute on the nodes that hold the data (data locality). A standby NameNode avoids a single point of failure; without one, losing the NameNode stops the cluster.
2. **Size raw disk:** usable data after compression × replication factor ÷ (1 − headroom) ÷ disk usable per node = DataNodes. Add temporary space for shuffle and intermediate data (often 20 to 30%). Project over the retention window with growth. Run `scripts/hdfs_sizing.py`.
3. **Check NameNode memory.** Each file, directory and block uses about 150 bytes of heap. Millions of tiny files exhaust the NameNode long before disks fill, and each one also becomes its own task in a job. The script reports object count and heap needed.
4. **Fix small files.** Compact on ingest into files of about one block size, write with fewer output partitions, use container formats (Parquet, ORC, Avro, sequence files), or partition less finely.
5. **Plan for failure.** With replication 3 and rack awareness (one replica on a different rack), a whole rack can fail without data loss. Leave enough free space to re-replicate a failed node's blocks.
6. **Choose the block size.** Larger blocks (256 MB or more) suit large sequential scans and reduce metadata; they do not help small files.
7. **Question the platform.** HDFS suits large, append-mostly files read sequentially by compute sitting on the same nodes. It is a poor fit for random updates, low-latency lookups, many small files, or bursty workloads. Object storage with separate compute usually wins in the cloud; datastore-selection covers which store to use.

## Deliverable

**Part A: Sizing brief**, for the budget owner

- Nodes and raw storage needed now and at the end of the planning horizon.
- The main risk (NameNode memory, small files, rack failure, growth) and its fix.
- Whether to stay on a cluster or move to object storage, with the cost logic.

**Part B: Capacity appendix**, for the engineers

- The sizing calculation with every assumption.
- Object and block counts, and NameNode heap needed.
- Replication, rack layout and compaction plan.

## Traps

- Forgetting replication, so the cluster holds a third of what was planned.
- Sizing to 100% full, leaving no room to re-replicate after a failure.
- Planning on bytes while file count exhausts NameNode memory.
- Assuming compression ratios without testing on real data.
- Running an always-on cluster in the cloud for a few hours of daily jobs.
- A single NameNode with no standby for a production cluster.
