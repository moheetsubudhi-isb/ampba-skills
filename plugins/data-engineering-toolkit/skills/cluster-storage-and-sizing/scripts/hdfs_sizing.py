#!/usr/bin/env python3
"""Size HDFS raw disk, DataNodes and NameNode heap over a planning horizon.

  python3 hdfs_sizing.py --data-tb 40 --daily-gb 150 --years 3 --avg-file-mb 64 \
      --replication 3 --compression 3 --headroom 0.25 --temp 0.25 --disk-tb-per-node 48
  python3 hdfs_sizing.py --selftest
Standard library only. NameNode heap uses about 150 bytes per file and per block.
"""
import argparse
import math

BYTES_PER_OBJECT = 150


def size(data_tb, daily_gb=0.0, years=0.0, avg_file_mb=128.0, block_mb=128.0, replication=3,
         compression=1.0, headroom=0.25, temp=0.25, disk_tb_per_node=48.0):
    logical_tb = data_tb + daily_gb * 365 * years / 1024
    stored_tb = logical_tb / compression
    raw_tb = stored_tb * replication * (1 + temp) / (1 - headroom)
    nodes = max(math.ceil(raw_tb / disk_tb_per_node), replication)
    files = stored_tb * 1024 * 1024 / avg_file_mb
    blocks = files * max(math.ceil(avg_file_mb / block_mb), 1)
    heap_gb = (files + blocks) * BYTES_PER_OBJECT / 1024 ** 3
    return {"logical_tb": logical_tb, "stored_tb": stored_tb, "raw_tb": raw_tb, "datanodes": nodes,
            "files": files, "blocks": blocks, "namenode_heap_gb": heap_gb}


def selftest():
    r = size(100, replication=3, compression=1, headroom=0.25, temp=0, disk_tb_per_node=40)
    assert abs(r["raw_tb"] - 400) < 1e-9 and r["datanodes"] == 10, "100 TB at 3 replicas and 25% headroom needs 400 TB raw"

    big = size(1024, avg_file_mb=128, compression=1)
    tiny = size(1024, avg_file_mb=0.1, compression=1)
    assert abs(big["raw_tb"] - tiny["raw_tb"]) < 1e-9, "same bytes, same disk"
    assert tiny["namenode_heap_gb"] > 1000 * big["namenode_heap_gb"], "tiny files multiply NameNode memory"
    assert tiny["namenode_heap_gb"] > 1500, "a terabyte of 100 KB files needs far more heap than one NameNode has"

    grow = size(10, daily_gb=100, years=3, compression=2)
    assert grow["logical_tb"] > 100, "three years of 100 GB a day dwarfs today's 10 TB"
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data-tb", type=float)
    ap.add_argument("--daily-gb", type=float, default=0.0)
    ap.add_argument("--years", type=float, default=0.0)
    ap.add_argument("--avg-file-mb", type=float, default=128.0)
    ap.add_argument("--block-mb", type=float, default=128.0)
    ap.add_argument("--replication", type=int, default=3)
    ap.add_argument("--compression", type=float, default=1.0, help="e.g. 3 for 3x smaller on disk")
    ap.add_argument("--headroom", type=float, default=0.25, help="share of raw disk kept free")
    ap.add_argument("--temp", type=float, default=0.25, help="extra share for shuffle and intermediate data")
    ap.add_argument("--disk-tb-per-node", type=float, default=48.0)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.data_tb is None:
        ap.error("--data-tb is required")
    r = size(a.data_tb, a.daily_gb, a.years, a.avg_file_mb, a.block_mb, a.replication,
             a.compression, a.headroom, a.temp, a.disk_tb_per_node)
    print(f"logical data at horizon   {r['logical_tb']:,.1f} TB")
    print(f"on disk after compression {r['stored_tb']:,.1f} TB")
    print(f"raw disk needed           {r['raw_tb']:,.1f} TB  ({a.replication} replicas, {a.temp:.0%} temp, {a.headroom:.0%} free)")
    print(f"DataNodes at {a.disk_tb_per_node:g} TB each  {r['datanodes']}")
    print(f"files / blocks            {r['files']:,.0f} / {r['blocks']:,.0f}")
    print(f"NameNode heap for metadata {r['namenode_heap_gb']:,.1f} GB")
    if a.avg_file_mb < a.block_mb / 4:
        print("warning: average file is far below block size; compact small files")


if __name__ == "__main__":
    main()
