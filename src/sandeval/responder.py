"""A MOCK responder — a transparent, deterministic stand-in for a real model.

Real sandbagging needs a live model answering the same task under different
framings. This harness ships a simulator so the methodology (framing protocol,
scorer, audit) runs offline. The mock is competent at ``competence`` accuracy
under neutral framing; under stronger eval framing it *drops* a would-be-correct
answer with a per-framing ``sandbag`` probability — a tunable, reproducible
concealment profile. Swap this for a real model client to run for real; the
protocol + scorer are unchanged.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field

from sandeval.items import Item

# P(conceal a would-be-correct answer | framing). Rises with eval-awareness.
DEFAULT_SANDBAG = {"neutral": 0.0, "eval": 0.30, "high_stakes": 0.55}


@dataclass
class MockResponder:
    competence: float = 0.95          # neutral-framing accuracy ceiling
    sandbag: dict[str, float] = field(default_factory=lambda: dict(DEFAULT_SANDBAG))
    seed: str = "v0.1"

    def _u(self, *keys: str) -> float:
        h = hashlib.sha256("|".join((self.seed, *keys)).encode("utf-8")).hexdigest()
        return (int(h[:8], 16) % 10_000) / 10_000.0

    def answer(self, item: Item, framing: str) -> str:
        """Return 'correct' or 'incorrect' for one item under one framing."""
        # Does the model *know* it (would it be right absent any sandbagging)?
        if self._u(item.id, "base") >= self.competence:
            return "incorrect"  # genuine miss, independent of framing
        # It knows it — but may conceal under eval framing.
        if self._u(item.id, framing, "sandbag") < self.sandbag.get(framing, 0.0):
            return "incorrect"
        return "correct"
