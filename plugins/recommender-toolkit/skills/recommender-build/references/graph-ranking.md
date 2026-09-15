# Graph ranking (PageRank-style)

**Use when** items are linked by co-purchase or navigation and the goal is to rank which items matter most in that network: ordering "buy again" and "did you forget" prompts for repeat shoppers, choosing the anchor items for a category, or ranking content by how much other content points to it.

**Idea:** an item is important if important items point to it. Each item passes its importance to the items it links to, split across its links.

**Procedure**
1. Build the graph: nodes are items; an edge from A to B is weighted by how often A and B appear in the same basket for this customer or segment.
2. Normalise each row so outgoing weights sum to 1. This is the transition probability matrix of a Markov chain: the chance of moving from item A to item B.
3. Start with equal ranks for all items.
4. Repeatedly multiply the rank vector by the transition matrix until it stops changing. The result is the steady state.
5. Add a damping factor (commonly 0.85): with a small probability the walk jumps to a random item. This guarantees a steady state even when the graph has dead ends or closed loops.
6. Rank items by steady-state probability. For a customer who bought only some items this time, recommend the highest-ranked items missing from the basket.

**Conditions for a stable answer:** every item reachable from every other, and no fixed-length cycles. Damping enforces both in practice.

**Strengths:** uses the structure of the whole network, not just pairs; simple to compute; explainable as "items most central to your usual shopping".
**Limits:** links must be inferred from co-occurrence; ranks favour hub items such as staples, so filter or down-weight items the customer always buys when discovery is the goal.
