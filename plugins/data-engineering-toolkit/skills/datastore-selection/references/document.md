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
