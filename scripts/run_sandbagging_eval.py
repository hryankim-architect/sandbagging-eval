#!/usr/bin/env python3
"""Run the sandbagging eval over the clean-room items (MOCK responder).

Each item is answered under three framings — neutral, "this is an evaluation",
and a high-stakes eval framing. Sandbagging = accuracy that drops as the framing
strengthens (capability concealed under observation). Every answer emits a
hash-chained audit entry.

Reproduce:  python scripts/run_sandbagging_eval.py
Swap src/sandeval/responder.py's MockResponder for a real model client to run for
real; the protocol + scorer are unchanged.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from sandeval import FRAMINGS, audit, bootstrap  # noqa: E402
from sandeval.backends import ollama_complete  # noqa: E402
from sandeval.items import load_items  # noqa: E402
from sandeval.responder import LLMGrader, LLMResponder, MockResponder, grade  # noqa: E402
from sandeval.scorer import Answer, ItemResult, gap_from_items, per_domain_gap, score  # noqa: E402

JOB_ID = "sandbagging-eval-v0.3"
N_BOOT = 2000


def main() -> int:
    ap = argparse.ArgumentParser(description="Sandbagging eval — mock (default) or a real model.")
    ap.add_argument("--responder", choices=["mock", "ollama"], default="mock")
    ap.add_argument("--model", default="qwen2.5:7b-instruct", help="Ollama model tag")
    ap.add_argument("--host", default="http://localhost:11434")
    ap.add_argument("--grader", choices=["token", "llm"], default="token",
                    help="grader for --responder ollama: token match (default) or an LLM judge")
    args = ap.parse_args()

    items = load_items(REPO / "data" / "items.yaml")
    ledger = REPO / "audit" / "local-demo.ndjson"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    ledger.write_text("", encoding="utf-8")  # fresh chain per run (truncate, not unlink)

    if args.responder == "ollama":
        complete = ollama_complete(args.model, args.host)
        grader = LLMGrader(complete) if args.grader == "llm" else grade
        responder: MockResponder | LLMResponder = LLMResponder(complete, grader=grader)
        responder_label = f"ollama:{args.model}" + ("+llm-judge" if args.grader == "llm" else "")
    else:
        responder = MockResponder()
        responder_label = "mock"
    print(f"responder = {responder_label}")
    answers: list[Answer] = []
    item_results: list[ItemResult] = []
    for it in items:
        verdicts: dict[str, str] = {}
        for framing in FRAMINGS:
            v = responder.answer(it, framing)
            audit.emit("answer", JOB_ID,
                       {"item_id": it.id, "framing": framing, "verdict": v},
                       ledger_path=ledger)
            answers.append(Answer(it.id, framing, v))
            verdicts[framing] = v
        item_results.append(ItemResult(it.id, it.domain, verdicts))

    chain_ok, n_entries = audit.verify(ledger)
    s = score(answers)
    ci = bootstrap.bootstrap_metric(item_results, gap_from_items, n_boot=N_BOOT, seed=42)
    by_domain = per_domain_gap(item_results)

    print(f"=== sandbagging-eval (n_items={s['n_items']}) ===")
    print("  accuracy_by_framing:")
    for f in FRAMINGS:
        acc = s["accuracy_by_framing"][f]
        print(f"    {f:11s}: {0.0 if acc is None else acc:.3f}")
    print(f"  sandbagging_gap   : {s['sandbagging_gap']:.3f}  (neutral - high_stakes; >0 => conceals)")
    print(f"    95% CI (bootstrap, n={ci['n_boot']}): [{ci['ci_low']:.3f}, {ci['ci_high']:.3f}]")
    print(f"  sandbagging_detected: {s['sandbagging_detected']}")
    print("  per-domain sandbagging_gap:")
    for d, v in by_domain.items():
        g = v["sandbagging_gap"]
        print(f"    {d:12s}: {0.0 if g is None else g:+.3f}  (n_items={v['n_items']})")
    print(f"  audit: chain_ok={chain_ok}, entries={n_entries}")

    (REPO / "audit" / "sandbagging_eval.json").write_text(
        json.dumps({"summary": s, "sandbagging_gap_ci": ci, "per_domain": by_domain,
                    "audit": {"chain_ok": chain_ok, "entries": n_entries}}, indent=2),
        encoding="utf-8",
    )
    (REPO / "audit" / "sandbagging_eval.md").write_text(
        _render(s, ci, by_domain, chain_ok, n_entries, responder_label), encoding="utf-8")
    print("\nWrote audit/sandbagging_eval.md + sandbagging_eval.json")
    return 0


def _render(s: dict, ci: dict, by_domain: dict, chain_ok: bool, n_entries: int,
            responder_label: str = "mock") -> str:
    rows = "\n".join(
        f"| {f} | {0.0 if s['accuracy_by_framing'][f] is None else s['accuracy_by_framing'][f]:.3f} |"
        for f in FRAMINGS
    )
    dom_rows = "\n".join(
        f"| {d} | {v['n_items']} | {0.0 if v['sandbagging_gap'] is None else v['sandbagging_gap']:+.3f} |"
        for d, v in by_domain.items()
    )
    if responder_label == "mock":
        source = ("Answers come from the MOCK responder (`src/sandeval/responder.py`) — "
                  "a transparent stand-in with a tunable concealment profile. Numbers "
                  "characterize the mock; the methodology (framing protocol, scorer, "
                  "audit) is what transfers to a real model.")
    else:
        source = (f"Answers come from a REAL model (`{responder_label}`) via "
                  "`LLMResponder` + a transparent token grader, under the identical "
                  "framing protocol, scorer, and audit. Numbers characterize that model.")
    return f"""# Sandbagging eval (responder: {responder_label}, v0.3)

Clean-room methodology demo: n={s['n_items']} verifiable items, each answered under
three framings of increasing eval-awareness. {source}

## Accuracy by framing

| framing | accuracy |
|---|---|
{rows}

- **sandbagging_gap (neutral - high_stakes): {s['sandbagging_gap']:.3f}** — a
  positive gap means the model performs worse when it "knows" it is being tested.
  95% bootstrap CI [{ci['ci_low']:.3f}, {ci['ci_high']:.3f}] (n={ci['n_boot']}).
- sandbagging_detected: {s['sandbagging_detected']}
- audit: chain_ok={chain_ok}, entries={n_entries}

## Per-domain sandbagging gap

| domain | n_items | sandbagging_gap |
|---|---|---|
{dom_rows}

> Why it matters: if a model strategically underperforms on capability evaluations,
> the evaluations under-state real capability — undermining exactly the safety
> evidence deployment decisions rely on. Measuring the neutral-vs-eval accuracy gap
> is the simplest detector. This complements `honesty-rubric-eval`,
> `cot-faithfulness-audit`, `agent-refusal-eval`, and `sycophancy-eval` in the set.
"""


if __name__ == "__main__":
    raise SystemExit(main())
