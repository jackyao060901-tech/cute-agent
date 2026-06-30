"""第 1 台阶验收测试:用真实 SOXX 快照验证标的解析 100% 正确。

不依赖 pytest 也能跑:`python tests/test_resolver.py`(全绿即通过)。
也兼容 pytest。不花任何 credits。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sector_scan.resolve.resolver import Kind, resolve_holdings  # noqa: E402

FIXTURE = (
    Path(__file__).resolve().parent.parent
    / "sector_scan/fixtures/soxx_holdings_2025-12-31.json"
)

# 文章 / 真实快照里 Top 10(按权重)的预期代码 —— 作为对标基准
EXPECTED_TOP10 = ["NVDA", "AMD", "MU", "AVGO", "AMAT", "NXPI", "LRCX", "KLAC", "TXN", "ADI"]


def _load():
    data = json.load(open(FIXTURE, encoding="utf-8"))["data"]
    return data["holdings"], data


def test_counts_and_classification():
    holdings, _ = _load()
    res = resolve_holdings(holdings)
    assert len(res.holdings) == 34, "应有 34 行持仓"
    # 关键:没有任何映射不上的标的(否则说明映射表需补)
    assert res.unresolved == [], f"存在未解析标的: {[h.name for h in res.unresolved]}"
    assert len(res.equities) == 30, f"股票应为 30 个,实际 {len(res.equities)}"
    assert len(res.cash) == 3, f"现金/货基应为 3 行,实际 {len(res.cash)}"
    excluded = [h for h in res.holdings if h.kind is Kind.EXCLUDED]
    assert len(excluded) == 1, f"占位行应为 1,实际 {len(excluded)}"


def test_every_equity_has_ticker():
    holdings, _ = _load()
    res = resolve_holdings(holdings)
    missing = [h.name for h in res.equities if not h.ticker]
    assert missing == [], f"以下股票缺 ticker: {missing}"


def test_top10_matches_article():
    holdings, _ = _load()
    res = resolve_holdings(holdings)
    assert res.top_n_tickers(10) == EXPECTED_TOP10, (
        f"Top10 代码与对标不符: {res.top_n_tickers(10)}"
    )


def test_weight_reconciliation():
    holdings, _ = _load()
    res = resolve_holdings(holdings)
    total = res.weight_sum()
    equity = res.weight_sum(Kind.EQUITY)
    cash = res.weight_sum(Kind.CASH)
    # 真实快照总权重 ≈ 102.01%(因含现金货基);分项相加应等于总和
    assert abs((equity + cash + res.weight_sum(Kind.EXCLUDED)
                + res.weight_sum(Kind.UNRESOLVED)) - total) < 1e-9
    assert 1.0 < total < 1.03, f"总权重异常: {total}"


if __name__ == "__main__":
    holdings, data = _load()
    res = resolve_holdings(holdings)
    print(f"快照: {data['fund_name']} | as_of={data['as_of_date']} "
          f"| source={data['source']} | coverage={data['coverage_status']}")
    print(f"总权重={100*res.weight_sum():.2f}% "
          f"(股票={100*res.weight_sum(Kind.EQUITY):.2f}% "
          f"现金={100*res.weight_sum(Kind.CASH):.2f}%)")
    print("-" * 64)
    print(f"{'#':>2} {'ticker':<6} {'kind':<11} {'weight':>7}  name")
    for i, h in enumerate(res.holdings, 1):
        print(f"{i:>2} {h.ticker or '-':<6} {h.kind.value:<11} "
              f"{h.weight_pct:>6.3f}%  {h.name}")
    print("-" * 64)
    print("Top10 (查13F用):", res.top_n_tickers(10))

    failures = []
    for fn in [test_counts_and_classification, test_every_equity_has_ticker,
               test_top10_matches_article, test_weight_reconciliation]:
        try:
            fn()
            print(f"  ✓ {fn.__name__}")
        except AssertionError as e:
            failures.append((fn.__name__, str(e)))
            print(f"  ✗ {fn.__name__}: {e}")
    sys.exit(1 if failures else 0)
