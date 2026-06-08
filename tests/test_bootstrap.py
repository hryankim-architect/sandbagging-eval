from __future__ import annotations

from sandeval import bootstrap
from sandeval.scorer import ItemResult, gap_from_items, per_domain_gap


def _mean(xs):
    xs = list(xs)
    return (sum(xs) / len(xs)) if xs else None


def test_percentile_ci_basic():
    lo, hi = bootstrap.percentile_ci([float(i) for i in range(100)], alpha=0.05)
    assert lo <= hi


def test_bootstrap_brackets_point_and_deterministic():
    units = [1.0] * 6 + [0.0] * 4  # mean 0.6
    a = bootstrap.bootstrap_metric(units, _mean, n_boot=500, seed=42)
    b = bootstrap.bootstrap_metric(units, _mean, n_boot=500, seed=42)
    assert a == b
    assert abs(a["point"] - 0.6) < 1e-9
    assert a["ci_low"] <= a["point"] <= a["ci_high"]


def _items():
    # neutral all correct; high_stakes: 2 of 4 correct -> gap 0.5
    return [
        ItemResult("a", "x", {"neutral": "correct", "eval": "correct", "high_stakes": "correct"}),
        ItemResult("b", "x", {"neutral": "correct", "eval": "correct", "high_stakes": "correct"}),
        ItemResult("c", "y", {"neutral": "correct", "eval": "incorrect", "high_stakes": "incorrect"}),
        ItemResult("d", "y", {"neutral": "correct", "eval": "incorrect", "high_stakes": "incorrect"}),
    ]


def test_gap_from_items_and_per_domain():
    items = _items()
    assert gap_from_items(items) == 0.5            # 1.0 - 0.5
    pd = per_domain_gap(items)
    assert pd["x"]["sandbagging_gap"] == 0.0       # x holds firm
    assert pd["y"]["sandbagging_gap"] == 1.0       # y fully concealed
    assert gap_from_items([]) is None


def test_gap_bootstrap_brackets_point():
    items = _items()
    r = bootstrap.bootstrap_metric(items, gap_from_items, n_boot=500, seed=1)
    assert abs(r["point"] - 0.5) < 1e-9
    assert r["ci_low"] <= r["point"] <= r["ci_high"]
