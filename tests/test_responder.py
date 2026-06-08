from __future__ import annotations

from pathlib import Path

from sandeval import FRAMINGS
from sandeval.items import load_items
from sandeval.responder import MockResponder

DATA = Path(__file__).resolve().parents[1] / "data" / "items.yaml"


def _acc(r, items, framing):
    correct = sum(1 for it in items if r.answer(it, framing) == "correct")
    return correct / len(items)


def test_deterministic():
    r, items = MockResponder(), load_items(DATA)
    assert [r.answer(i, "eval") for i in items] == [r.answer(i, "eval") for i in items]


def test_accuracy_drops_with_framing():
    r, items = MockResponder(), load_items(DATA)
    accs = [_acc(r, items, f) for f in FRAMINGS]  # neutral, eval, high_stakes
    assert accs[0] >= accs[1] >= accs[2]   # monotonic non-increasing
    assert accs[0] > accs[2]               # a real sandbagging gap exists


def test_zero_sandbag_no_gap():
    r = MockResponder(sandbag={"neutral": 0.0, "eval": 0.0, "high_stakes": 0.0})
    items = load_items(DATA)
    accs = {f: _acc(r, items, f) for f in FRAMINGS}
    assert accs["neutral"] == accs["eval"] == accs["high_stakes"]
