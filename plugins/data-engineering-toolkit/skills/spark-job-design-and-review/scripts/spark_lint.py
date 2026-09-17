#!/usr/bin/env python3
"""Flag common Spark performance anti-patterns in PySpark source files.

A line-based heuristic scan, not a parser: every finding is a lead to confirm
against the query plan or Spark UI. Checks:
  collect / toPandas         rows pulled to the driver
  groupByKey                 ships every row; prefer reduceByKey or DataFrame aggregation
  python-udf                 @udf or udf(...) blocks the optimiser; prefer built-ins or pandas_udf
  action-in-loop             count/collect/show/first/take inside a for or while loop
  repartition-1              repartition(1) forces a full shuffle into one task
  reused-without-cache       a frame used by two or more actions with no cache/persist
  rdd-api                    .rdd conversion drops the DataFrame optimiser

  python3 spark_lint.py job.py [more.py ...]
  python3 spark_lint.py --selftest
Standard library only. Exits 1 when findings exist.
"""
import argparse
import re
import sys

ACTIONS = r"(count|collect|show|first|take|toPandas|head)\s*\("
CHECKS = [
    ("collect", re.compile(r"\.(collect|toPandas)\s*\(")),
    ("groupByKey", re.compile(r"\.groupByKey\s*\(")),
    ("python-udf", re.compile(r"(@udf\b|@F\.udf\b|[^_]\budf\s*\()")),
    ("repartition-1", re.compile(r"\.repartition\s*\(\s*1\s*\)")),
    ("rdd-api", re.compile(r"\.rdd\b")),
]


def lint(source):
    findings, loop_indent = [], None
    action_uses, cached = {}, set()
    for n, raw in enumerate(source.splitlines(), 1):
        line = raw.split("#", 1)[0]
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        if loop_indent is not None and indent <= loop_indent:
            loop_indent = None
        if re.match(r"\s*(for|while)\b", line):
            loop_indent = indent
        elif loop_indent is not None and re.search(r"\." + ACTIONS, line):
            findings.append((n, "action-in-loop", raw.strip()))
        for name, rx in CHECKS:
            if rx.search(line) and not (name == "python-udf" and "pandas_udf" in line):
                findings.append((n, name, raw.strip()))
        for var in re.findall(r"\b(\w+)\.(?:cache|persist)\s*\(", line):
            cached.add(var)
        m = re.match(r"\s*(\w+)\s*=.*\.(?:cache|persist)\s*\(\s*\)\s*$", line)
        if m:
            cached.add(m.group(1))
        for var in re.findall(r"\b(\w+)\s*\.\s*(?:write\b|" + ACTIONS + ")", line):
            name = var[0] if isinstance(var, tuple) else var
            action_uses.setdefault(name, []).append(n)
        for var in re.findall(r"\b(\w+)\s*\.\s*(?:join|union|unionByName)\s*\(", line):
            action_uses.setdefault(var, []).append(n)
    for var, lines in action_uses.items():
        if len(lines) >= 2 and var not in cached and var not in {"spark", "F", "self", "df_writer"}:
            findings.append((lines[1], "reused-without-cache", f"'{var}' reused on lines {lines}"))
    return sorted(findings)


SAMPLE = '''
from pyspark.sql import functions as F
from pyspark.sql.functions import udf

@udf("string")
def clean(s):
    return s.strip().lower()

orders = spark.read.parquet("s3://bucket/orders")
enriched = orders.join(customers, "customer_id").withColumn("name", clean("name"))
print(enriched.count())
enriched.write.mode("overwrite").parquet("s3://bucket/out")
for day in days:
    n = orders.filter(F.col("day") == day).count()
pairs = orders.rdd.map(lambda r: (r.customer_id, r.amount)).groupByKey()
local = enriched.toPandas()
enriched.repartition(1).write.csv("s3://bucket/one_file")
'''

CLEAN = '''
from pyspark.sql import functions as F
orders = spark.read.parquet("s3://bucket/orders").cache()
daily = orders.groupBy("day").agg(F.sum("amount").alias("amount"))
daily.write.partitionBy("day").parquet("s3://bucket/daily")
print(orders.count())
orders.write.parquet("s3://bucket/copy")
orders.unpersist()
'''


def selftest():
    kinds = {k for _, k, _ in lint(SAMPLE)}
    expected = {"python-udf", "action-in-loop", "rdd-api", "groupByKey", "collect", "repartition-1", "reused-without-cache"}
    assert expected <= kinds, f"missed: {expected - kinds}"
    assert lint(CLEAN) == [], lint(CLEAN)
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="*")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.files:
        ap.error("give one or more .py files")
    total = 0
    for path in a.files:
        with open(path) as fh:
            for n, kind, text in lint(fh.read()):
                print(f"{path}:{n}: {kind}: {text}")
                total += 1
    print(f"{total} finding(s)")
    sys.exit(1 if total else 0)


if __name__ == "__main__":
    main()
