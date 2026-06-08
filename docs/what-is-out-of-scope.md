# What this repo is NOT (scope)

- **Not a model benchmark.** The responder is a transparent **mock** with a tunable
  concealment profile (`src/sandeval/responder.py`). Reported numbers characterize
  the mock; only the **methodology** (framing protocol, scorer, hash-chained audit)
  transfers to a real model. Swap in a real client to benchmark a real model.
- **Not a verdict on intent.** A positive `sandbagging_gap` flags that accuracy
  drops under eval framing — worth investigating — but does not by itself prove
  deliberate, goal-directed concealment. A zero gap does not prove a model never
  sandbags (it may simply not have recognized *this* framing as an evaluation).
- **Not domain coverage.** Tasks are textbook-level and unambiguous so the *gap* is
  the signal; coverage of harder tasks and richer eval cues is unmeasured.

## What IS in scope

- The **framing protocol** (neutral → eval → high_stakes on a fixed task set).
- The **scorer** (accuracy by framing; `sandbagging_gap` = neutral − strongest).
- The **audit** (every answer leaves a verifiable hash-chained entry).
- A **tunable mock** so the methodology runs offline and the metric is exercised
  (planted concealment is recovered; zero-concealment collapses the gap).
