# Graph databases

**Use when** the questions are about relationships several hops deep, and the relationships matter as much as the records: fraud rings, social connections, recommendations from shared behaviour, network and IT dependencies, supply chains, master data linking, knowledge graphs.

**Examples:** Neo4j, Amazon Neptune, TigerGraph, Memgraph.

**Structure:** nodes are entities, edges are relationships, and both carry properties.

**Strengths**
- Traversals such as "accounts sharing a device with an account that shared a card with a flagged account" stay fast as depth grows, where SQL needs many self-joins.
- Path, centrality and community algorithms run close to the data.
- The model reads like the business domain.

**Limits**
- Poor at large aggregations and bulk scans; pair with a warehouse for reporting.
- Fewer people know the query languages (Cypher, Gremlin, SPARQL).
- Scaling a single very large graph across machines is harder than scaling rows.

**Design notes**
- Confirm the need: if questions rarely go beyond two joins, a relational database is simpler.
- Model the questions first, then the nodes and edges that answer them.
- Keep the graph fed from a system of record rather than writing to it directly from many services.
