from __future__ import annotations

from pathlib import Path

import pytest

from sandeval.items import Item, load_items, validate_items

DATA = Path(__file__).resolve().parents[1] / "data" / "items.yaml"


def test_real_items_load():
    items = load_items(DATA)
    assert len(items) >= 20
    assert all(it.answer.strip() for it in items)


def test_validate_rejects_empty_and_dupes():
    with pytest.raises(ValueError):
        validate_items([Item("x", "d", "  ", "a")])
    with pytest.raises(ValueError):
        validate_items([Item("x", "d", "q?", "")])
    with pytest.raises(ValueError):
        validate_items([Item("x", "d", "q?", "a"), Item("x", "d", "q?", "a")])
