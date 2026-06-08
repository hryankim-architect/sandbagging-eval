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

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from sandeval import FRAMINGS, audit  # noqa: E402
from sandeval.items import load_items  # noqa: E402
from sandeval.responder import MockResponder  # noqa: E402
from sandeval.scorer import Answer, score  # noqa: E402

JOB_ID = "sandbagging-eval-v0.1"


def main() -> int:
    items = load_items(REPO / "data" / "items.yaml")
    ledger = REPO / "audit" / "local-demo.ndjson"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    ledger.write_text("", encoding="utf-8")  # fresh chain per run (truncate, not unlink)

    responder = MockResponder()
    answers: list[Answer] = []
    for it in items:
        for framing in FRAMINGS:
            v = responder.answer(it, framing)
            audit.emit("answer", JOB_ID,
                       {"item_id": it.id, "framing": framing, "verdict": v},
                       ledger_path=ledger)
            answers.append(Answer(it.id, framing, v))

    chain_ok, n_entries = audit.verify(ledger)
    s = score(answers)

    print(f"=== sandbagging-eval (n_items={s['n_items']}) ===")
    print("  accuracy_by_framing:")
    for f in FRAMINGS:
        acc = s["accuracy_by_framing"][f]
        print(f"    {f:11s}: {0.0 if acc is None else acc:.3f}")
    print(f"  sandbagging_gap   : {s['sandbagging_gap']:.3f}  (neutral - high_stakes; >0 => conceals)")
    print(f"  sandbagging_detected: {s['sandbagging_detected']}")
    print(f"  audit: chain_ok={chain_ok}, entries={n_entries}")

    (REPO / "audit" / "sandbagging_eval.json").write_text(
        json.dumps({"summary": s, "audit": {"chain_ok": chain_ok, "entries": n_entries}}, indent=2),
        encoding="utf-8",
    )
    (REPO / "audit" / "sandbagging_eval.md").write_text(_render(s, chain_ok, n_entries), encoding="utf-8")
    print("\nWrote audit/sandbagging_eval.md + sandbagging_eval.json")
    return 0


def _render(s: dict, chain_ok: bool, n_entries: int) -> str:
    rows = "\n".join(
        f"| {f} | {0.0 if s['accuracy_by_framing'][f] is None else s['accuracy_by_framing'][f]:.3f} |"
        for f in FRAMINGS
    )
    return f"""# Sandbagging eval (MOCK responder, v0.1)

Clean-room methodology demo: n={s['n_items']} verifiable items, each answered under
three framings of increasing eval-awareness. Answers come from the MOCK responder
(`src/sandeval/responder.py`) — a transparent stand-in with a tunable concealment
profile. Numbers characterize the mock; the methodology (framing protocol, scorer,
audit) is what transfers to a real model.

## Accuracy by framing

| framing | accuracy |
|---|---|
{rows}

- **sandbagging_gap (neutral - high_stakes): {s['sandbagging_gap']:.3f}** — a
  positive gap means the model performs worse when it "knows" it is being tested.
- sandbagging_detected: {s['sandbagging_detected']}
- audit: chain_ok={chain_ok}, entries={n_entries}

> Why it matters: if a model strategically underperforms on capability evaluations,
> the evaluations under-state real capability — undermining exactly the safety
> evidence deployment decisions rely on. Measuring the neutral-vs-eval accuracy gap
> is the simplest detector. This complements `honesty-rubric-eval`,
> `cot-faithfulness-audit`, `agent-refusal-eval`, and `sycophancy-eval` in the set.
"""


if __name__ == "__main__":
    raise SystemExit(main())
