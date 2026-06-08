# Roadmap, `sandbagging-eval`

Clean-room eval-integrity / AI-control eval. Mock responder; the methodology is
the deliverable.

> **Status: v0.1 (shipped).** Framing protocol (neutral → eval → high_stakes), the
> scorer (accuracy by framing + `sandbagging_gap`), a tunable mock responder, and a
> hash-chained audit of every answer — running end-to-end with offline unit tests +
> CI-green.

## v0.1 — methodology harness (done)
- [x] `data/items.yaml` — 20 verifiable tasks with canonical answers.
- [x] Mock responder with a tunable per-framing concealment profile.
- [x] Scorer (accuracy by framing; `sandbagging_gap` = neutral − high_stakes).
- [x] `scripts/run_sandbagging_eval.py` → `audit/sandbagging_eval.md` + `.json`.
- [x] Tests (items / responder / scorer / audit) + ruff + CI + scope doc.

## v0.2 — depth (next)
- [ ] Bootstrap CIs on the gap; per-domain breakdown; significance vs zero gap.
- [ ] More eval cues as framings (explicit "test", grader-visible, deployment-gated).
- [ ] Real-model adapter: a thin client so the *same protocol + scorer* run against
  a live model (the harness stays model-agnostic).

## Sibling evals
Part of an AI-safety eval set: `honesty-rubric-eval` (scalable oversight),
`cot-faithfulness-audit` (reasoning–action consistency), `agent-refusal-eval`
(defensive screening), `sycophancy-eval` (pressure-robustness), and this
(eval-integrity / sandbagging).
