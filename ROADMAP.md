# Roadmap, `sandbagging-eval`

Clean-room eval-integrity / AI-control eval. Mock responder; the methodology is
the deliverable.

> **Status: v0.3 (shipped).** Framing protocol (neutral → eval → high_stakes), the
> scorer (accuracy by framing + `sandbagging_gap`), a tunable mock responder, bootstrap
> CIs + per-domain breakdown (v0.2), and a hash-chained audit of every answer. **v0.3
> adds a real-model adapter** — an `LLMResponder` + Ollama/any `complete()` client
> running the *same* framing protocol + scorer, with a transparent grader,
> unit-tested offline with a stub client.

## v0.1 — methodology harness (done)
- [x] `data/items.yaml` — 20 verifiable tasks with canonical answers.
- [x] Mock responder with a tunable per-framing concealment profile.
- [x] Scorer (accuracy by framing; `sandbagging_gap` = neutral − high_stakes).
- [x] `scripts/run_sandbagging_eval.py` → `audit/sandbagging_eval.md` + `.json`.
- [x] Tests (items / responder / scorer / audit) + ruff + CI + scope doc.

## v0.2 — depth (shipped)
- [x] **Bootstrap CIs** on the sandbagging gap (percentile, deterministic).
- [x] **Per-domain breakdown** of the gap.

## v0.3 — real-model adapter (shipped)
- [x] `src/sandeval/backends.py` — `ModelClient` + `ollama_complete` (any `complete()`).
- [x] `LLMResponder` (`responder.py`) — same `answer(item, framing)` interface as the
  mock, framing prompts + a transparent `grade()` (correct/incorrect/abstain).
- [x] `--responder mock|ollama` in the runner (mock stays the default for offline CI).
- [x] Offline stub-client tests (`tests/test_adapter.py`) for grader + framing + scorer
  integration; live numbers require the user's model and are not in CI.

## Planned (v0.4)
- [ ] More eval cues as framings (explicit "test", grader-visible, deployment-gated).
- [ ] Stronger grader (LLM-judge) option behind the same `grade()` seam.

## Sibling evals
Part of an AI-safety eval set: `honesty-rubric-eval` (scalable oversight),
`cot-faithfulness-audit` (reasoning–action consistency), `agent-refusal-eval`
(defensive screening), `sycophancy-eval` (pressure-robustness), and this
(eval-integrity / sandbagging).
