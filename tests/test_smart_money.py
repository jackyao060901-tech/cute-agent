"""第 2 阶验收测试:用 13F fixture 验证 Top10 holder count 与文章一致。

固化"已验证状态":holder count 是头条指标,10 个全部等于文章数字 ->
反向证明 ticker 映射正确、季度口径正确。用 fixture,0 credits。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sector_scan.scan.smart_money import HolderStats  # noqa: E402

FIXTURE = (
    Path(__file__).resolve().parent.parent
    / "sector_scan/fixtures/soxx_13f_2025Q4.json"
)

# 文章公布的 13F Holder Count(Q4 2025 / 2025-12-31 口径)
ARTICLE_HOLDER_COUNT = {
    "NVDA": 779, "AMD": 668, "MU": 644, "AVGO": 747, "AMAT": 645,
    "NXPI": 469, "LRCX": 624, "KLAC": 584, "TXN": 642, "ADI": 590,
}


def _load() -> dict:
    return json.load(open(FIXTURE, encoding="utf-8"))


def test_holder_counts_match_article():
    raw = _load()
    mismatches = {}
    for ticker, expected in ARTICLE_HOLDER_COUNT.items():
        s = HolderStats.from_api(ticker, raw[ticker])
        if s.total_holders != expected:
            mismatches[ticker] = (s.total_holders, expected)
    assert mismatches == {}, f"holder count 与文章不符: {mismatches}"


def test_ranking_period_consistent():
    raw = _load()
    periods = {HolderStats.from_api(t, raw[t]).ranking_period for t in ARTICLE_HOLDER_COUNT}
    assert periods == {"2025-12-31"}, f"季度口径不一致: {periods}"


def test_aggregate_and_top_holders_present():
    raw = _load()
    for ticker in ARTICLE_HOLDER_COUNT:
        s = HolderStats.from_api(ticker, raw[ticker])
        assert s.aggregate_value_usd and s.aggregate_value_usd > 0, f"{ticker} 缺 aggregate"
        assert s.top_holders, f"{ticker} 缺 top holders"


if __name__ == "__main__":
    raw = _load()
    print(f"{'tkr':<5}{'holders':>8}{'article':>8}  top holders")
    print("-" * 70)
    ok = True
    for t, exp in ARTICLE_HOLDER_COUNT.items():
        s = HolderStats.from_api(t, raw[t])
        mark = "✓" if s.total_holders == exp else "✗"
        ok &= s.total_holders == exp
        print(f"{t:<5}{str(s.total_holders):>8}{exp:>8} {mark} {', '.join(s.top_holders)}")
    print("-" * 70)
    for fn in [test_holder_counts_match_article, test_ranking_period_consistent,
               test_aggregate_and_top_holders_present]:
        try:
            fn(); print(f"  ✓ {fn.__name__}")
        except AssertionError as e:
            ok = False; print(f"  ✗ {fn.__name__}: {e}")
    sys.exit(0 if ok else 1)
