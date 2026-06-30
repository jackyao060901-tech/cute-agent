"""第 4 阶验收:集中度分层 + 重复暴露,确定性、可复核。用 fixture,0 credits。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sector_scan.resolve.resolver import resolve_holdings  # noqa: E402
from sector_scan.scan.compute import concentration, duplicate_exposure  # noqa: E402

FIXTURE = (
    Path(__file__).resolve().parent.parent
    / "sector_scan/fixtures/soxx_holdings_2025-12-31.json"
)


def _res():
    h = json.load(open(FIXTURE, encoding="utf-8"))["data"]["holdings"]
    return resolve_holdings(h)


def test_concentration_matches_article():
    c = concentration(_res(), core_n=5, top_n=10)
    assert abs(c.top_n_pct - 56.3) < 0.2, c.top_n_pct          # 文章 Top10 56.3%
    assert abs(c.core_pct - 35.6) < 0.2, c.core_pct            # 文章核心 35.6%
    assert abs(c.other_top_pct - 20.7) < 0.2, c.other_top_pct  # 文章 20.7%
    assert c.core_tickers == ["NVDA", "AMD", "MU", "AVGO", "AMAT"], c.core_tickers


def test_tiers_sum_to_total():
    c = concentration(_res())
    # 含剔除档:每一行(包括占位行)都对得上总额
    s = c.core_pct + c.other_top_pct + c.other_equity_pct + c.cash_pct + c.excluded_pct
    assert abs(s - c.total_pct) < 1e-6, (s, c.total_pct)


def test_duplicate_exposure_nvda():
    de = duplicate_exposure(_res(), "NVDA", invest_amount=100_000)
    assert de.found
    assert abs(de.weight_pct - 8.263) < 0.01, de.weight_pct
    assert abs(de.indirect_amount - 8263) < 5, de.indirect_amount  # 8.263% × $100k


def test_duplicate_exposure_not_in_etf():
    de = duplicate_exposure(_res(), "AAPL", invest_amount=100_000)
    assert not de.found and de.indirect_amount is None


if __name__ == "__main__":
    res = _res()
    c = concentration(res)
    print(f"集中度: Top{c.top_n}={c.top_n_pct:.2f}% 核心Top{c.core_n}={c.core_pct:.2f}% "
          f"({'/'.join(c.core_tickers)})")
    print("分档:")
    for label, pct in c.as_rows():
        print(f"  {label:<34} {pct:6.2f}%")
    print(f"  {'合计':<34} {c.total_pct:6.2f}%")
    de = duplicate_exposure(res, "NVDA", invest_amount=100_000)
    print(f"重复暴露: 持有 NVDA 再买 $100,000 SOXX → 间接增加 NVDA ${de.indirect_amount:,.0f} "
          f"(权重 {de.weight_pct:.2f}%)")
    ok = True
    for fn in [test_concentration_matches_article, test_tiers_sum_to_total,
               test_duplicate_exposure_nvda, test_duplicate_exposure_not_in_etf]:
        try:
            fn(); print(f"  ✓ {fn.__name__}")
        except AssertionError as e:
            ok = False; print(f"  ✗ {fn.__name__}: {e}")
    sys.exit(0 if ok else 1)
