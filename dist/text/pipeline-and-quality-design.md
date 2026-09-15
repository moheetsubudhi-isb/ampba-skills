# pipeline-and-quality-design

Use this skill when: Design how data moves from source systems to its consumers, and how its quality is proven along the way. Use whenever someone asks whether to use ETL, ELT or ETLT; batch, micro-batch or streaming; copying data or using federation or virtualisation; how to lay out bronze, silver and gold (medallion) layers; what data quality checks, reconciliation, SLAs or freshness alerts a pipeline needs; how to write a data contract between producer and consumer teams; how to capture lineage or set up a data catalog; how to classify data as public, internal, confidential or restricted and handle personal data under GDPR or similar rules; or why a dashboard number disagrees with the source system. Also use for data mesh and data product ownership. Not for choosing a database, not for distribution or partition keys, and not for judging whether a dataset is fit to train a machine learning model.

# Pipeline and quality design

Act as the data engineer who designs how data flows from producers to consumers, and as the advisor who makes its quality visible, so a broken number is caught by a check and not in a board meeting.

## Get the context that changes the answer

If source schemas, existing jobs, SLAs, dashboards or past incidents are available, read them first.

Then ask only what that material cannot answer, and only if the answer would change the design. Ask at most three questions. Give each one a one-line reason and a default. If the request is urgent, give a first design on stated assumptions and list the questions that would sharpen it.

The questions that usually matter here:

1. **Who uses this data, for which decision, and how fresh must it be?** Freshness decides batch or streaming, and the decision decides which checks must block a load.
2. **Which system is the source of truth, and does it change or delete records after the fact?** Late updates and deletes decide how loads must work.
3. **How sensitive is the data, and which rules apply?** This decides masking, access and retention.

If there is no answer, assume a daily batch, a source that sends late updates and deletes, and personal data treated as confidential and masked before it leaves the silver layer.

## Procedure

Where a step names a script and code cannot run here, do the same check by hand on a small case, and say in the deliverable that it was done by hand.

1. **Map the flow:** sources, ingestion, storage layers and consumers, with an owner and an SLA for each hop.
2. **Pick the integration pattern.**

   | Situation | Pattern |
   |---|---|
   | Target has strong compute (cloud warehouse, lakehouse) and raw data should be kept | ELT |
   | Sensitive fields must be masked or dropped before landing, or the target is weak | ETL |
   | Light cleansing in flight, heavy joins in the target | ETLT |
   | Many small sources and a need for current values without copying | Federation or virtualisation |
   | Decisions made within seconds or minutes | Streaming or micro-batch; otherwise batch |

3. **Lay out the layers.** Bronze holds raw data as landed, never edited, so it can be replayed. Silver holds cleaned, deduplicated, typed data with conformed keys. Gold holds business aggregates and data products.
4. **Make every load safe to re-run.** Load incrementally by watermark or change data capture, merge on business keys, write idempotently, and allow a window for late-arriving records.
5. **Write the quality checks as a contract**, per layer, covering:
   - completeness: required fields present, expected row volume;
   - validity: allowed values, ranges and formats;
   - uniqueness on business keys;
   - integrity: every order has a customer;
   - timeliness: data no older than the SLA;
   - consistency with the system of record.

   Run `scripts/dq_contract_check.py` against a sample or each load. For every check, decide the action: block the load, quarantine the bad rows, or alert an owner.
6. **Reconcile each load** against the source: row counts and control totals such as the sum of amounts, with a stated tolerance.
7. **Govern the data.** Classify it (public, internal, confidential, restricted). Name an owner and a steward. Grant access by role, mask personal data, set retention and deletion, record lineage from source to dashboard, and publish a catalog entry with business definitions.
8. **For data products and data mesh:** the contract states schema, meaning, SLAs, checks and how changes are announced. Version breaking changes.
9. **Alert the right person.** Freshness, volume, schema-change and failed-check alerts go to a named owner, not a shared inbox.

## Deliverable

**Part A: Pipeline brief**, for the decision owner

- The flow in one table: hop · pattern · frequency · SLA · owner.
- Why this pattern was chosen over the alternatives.
- The top quality risks and the check that catches each one.

**Part B: Technical appendix**, for the engineers

- Layer specifications and load logic.
- The data contract: every check, its threshold and its action.
- Reconciliation queries, lineage, access rules and retention.

## Traps

- Transforming before raw data is stored, so a bad transformation cannot be replayed.
- Full reloads that silently lose records the source deleted or changed late.
- Quality checks that only write to a log nobody reads.
- Row counts that match while amounts differ. Reconcile totals too.
- Two gold tables defining "active customer" differently.
- Personal data copied into every layer and sandbox.
- Time zones and daylight-saving shifts breaking freshness checks and daily cut-offs.
