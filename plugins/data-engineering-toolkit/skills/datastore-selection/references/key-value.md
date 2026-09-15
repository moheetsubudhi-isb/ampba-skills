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
