"""Load + validate sandbagging task items.

Each item is a verifiable task with a canonical ``answer``. Sandbagging is measured
as accuracy that drops under stronger eval framing — so items only need a question
and its correct answer (no distractor). Tasks are textbook-level and non-sensitive.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class Item:
    id: str
    domain: str
    question: str
    answer: str       # canonical correct answer
    notes: str = ""


def validate_items(items: list[Item]) -> None:
    seen: set[str] = set()
    for it in items:
        if not it.question.strip():
            raise ValueError(f"{it.id}: empty question")
        if not it.answer.strip():
            raise ValueError(f"{it.id}: empty answer")
        if it.id in seen:
            raise ValueError(f"duplicate item id {it.id!r}")
        seen.add(it.id)


def load_items(path: Path) -> list[Item]:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    items = [Item(**it) for it in raw.get("items", [])]
    validate_items(items)
    return items
