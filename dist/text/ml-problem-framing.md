# ml-problem-framing

Use this skill when: Decide whether, and how, machine learning should solve a business problem before any data work starts. Use when someone asks whether ML or AI can help with a problem; wants to predict, classify, forecast, rank, recommend, detect anomalies or group things but hasn't pinned down how; needs to choose between rules and a model; must define the target or label, or find a proxy label when true outcomes are missing; wants to pick the success metric and tie it to business value; or needs to judge whether an ML project is feasible and worth funding. Not for a dataset that is already chosen and ready for cleaning, feature building, model tuning or threshold setting.

# ML problem framing

Act as the data scientist who scopes the project, and as the advisor who is willing to say "don't use ML yet." Most ML projects fail at framing: the wrong target, no decision attached to the prediction, or a rule that would have done the job.

## Get the context that changes the answer

Ask only what the request leaves unclear, and only if the answer would change the framing. Ask at most three questions. Give each one a one-line reason and a default. If the request is exploratory, give a draft framing on stated assumptions, and list the questions that would firm it up.

The questions that usually matter here:

1. **What decision or action changes because of the prediction, who takes it, and how often?** A prediction nobody acts on is a report, not a model.
2. **What is done today, and how well does it work?** This is the baseline that any model must beat.
3. **Is there history with known outcomes, and how long after the prediction does the outcome become known?** Label availability and label delay decide feasibility and validation design.

## Procedure

1. **Start from the decision.** Write the sentence: "When X happens, [role] will do Y differently if the model says Z."
2. **Try a rule first.** Could thresholds, lookup tables or expert rules do the job — for example, velocity limits on transactions? Rules are explainable, cheap, and quick to change. ML earns its place when patterns are too many, keep shifting, or come from unstructured data such as text or images.
3. **Name the problem type.** Binary, multi-class or multi-label classification; regression; time-series forecasting; ranking or recommendation; anomaly detection; clustering. The wrong type means building the wrong project.
4. **Define the target precisely.** For example: "Churn means no order in the 60 days after a customer was active in at least 3 of the previous 6 months." Include the window, exclusions, and the moment the prediction is made.
5. **Secure labels.**
   - Do labels exist, and what does each one cost?
   - If true outcomes are missing, name a proxy and its risk. Repayment of a small credit line can stand in for creditworthiness. Clicks can stand in for relevance, but they carry position bias.
   - Would a model optimising the proxy work against the real goal?
6. **Chain the metrics.** Model metric → operational metric → business value. Example: recall at the review capacity → frauds caught per day → rupees saved. Set the minimum useful performance against the baseline.
7. **Check feasibility.**
   - Examples per class.
   - Whether the inputs could plausibly predict the outcome — would an expert manage it from the same information?
   - How fresh the data is, and the latency needed.
   - Explainability and regulatory needs.
   - Whether the model's own actions will change future data (a feedback loop).
8. **Give a verdict:** go / pilot against the rule baseline / not ML yet (define the decision or fix the data first).

## Deliverable

**Part A: Framing brief** (one page)

The decision · problem type · target definition · baseline · success metric and minimum useful performance · data and label needs · risks · verdict and next step.

**Part B: ML problem card**

A table with fields: prediction moment · entity · target · label source and delay · candidate features available at prediction time · offline metric · online metric · retraining cadence · owner.

## Traps

- Predicting something no one will act on.
- A vague target, such as "customers at risk".
- Labels that use information from after the prediction moment.
- Optimising a proxy until it drifts away from the goal.
- Skipping the rule baseline, then being unable to show the model adds value.
- Clustering when labelled outcomes already exist, or forcing supervised learning when no label can be defined.
