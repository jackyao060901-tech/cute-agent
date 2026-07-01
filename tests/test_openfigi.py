"""OpenFIGI 解析层测试:纯函数(离线,不联网)+ extra_map 合并路径。"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sector_scan.resolve.openfigi import _bad_ticker, _classify, _pick  # noqa: E402
from sector_scan.resolve.resolver import Kind, resolve_holdings  # noqa: E402


def test_classify_equity_vs_cash():
    assert _classify({"securityType": "Common Stock", "marketSector": "Equity"}) == "equity"
    assert _classify({"securityType": "ADR", "marketSector": "Equity"}) == "equity"
    assert _classify({"securityType": "Open-End Fund", "marketSector": "Equity"}) == "cash"
    assert _classify({"securityType": "Money Market Fund"}) == "cash"


def test_pick_only_us_and_clean():
    # 只取 exchCode=US 且合法 ticker;非 US 或垃圾一律不取
    assert _pick([{"ticker": "NVDA", "exchCode": "US"}])["ticker"] == "NVDA"
    assert _pick([{"ticker": "HONGBP", "exchCode": "X1"}]) is None   # 非US + 货币后缀
    assert _pick([{"ticker": "HONGBP", "exchCode": "US"}]) is None   # 即便标US,货币后缀也拒
    assert _pick([]) is None


def test_bad_ticker_guard():
    for bad in ["HONGBP", "TRI4EUR", "AZNN0", "TOOLONGX", "AB1"]:
        assert _bad_ticker(bad), bad
    for good in ["HON", "TRI", "AZN", "NVDA", "GOOGL", "BRKB"]:
        assert not _bad_ticker(good), good


def test_override_map_applied():
    # 外资/ADR override(Honeywell ISIN)应解析为 HON
    holdings = [{"holding_name": "Honeywell International Inc.", "isin": "US4385161066", "weight": 1.0}]
    res = resolve_holdings(holdings)
    assert res.equities and res.equities[0].ticker == "HON"


def test_extra_map_resolves_non_soxx():
    """SOXX 映射表外的标的,靠 extra_map(OpenFIGI 结果)解析。"""
    holdings = [
        {"holding_name": "Apple Inc", "isin": "US0378331005", "cusip": None, "weight": 0.5},
        {"holding_name": "Some MM Fund", "isin": "US000000MMF0", "cusip": None, "weight": 0.5},
    ]
    extra = {"US0378331005": ("AAPL", "equity"), "US000000MMF0": (None, "cash")}
    res = resolve_holdings(holdings, extra)
    assert res.equities and res.equities[0].ticker == "AAPL"
    assert len(res.cash) == 1
    assert res.unresolved == []


def test_soxx_map_takes_priority_over_extra():
    """SOXX 人工映射优先于 extra_map(可信度更高)。"""
    holdings = [{"holding_name": "NVIDIA Corp.", "isin": "US67066G1040", "weight": 1.0}]
    extra = {"US67066G1040": ("WRONG", "equity")}
    res = resolve_holdings(holdings, extra)
    assert res.equities[0].ticker == "NVDA"   # 用人工表的 NVDA,不用 extra 的 WRONG


if __name__ == "__main__":
    ok = True
    for fn in [test_classify_equity_vs_cash, test_pick_only_us_and_clean, test_bad_ticker_guard,
               test_override_map_applied, test_extra_map_resolves_non_soxx,
               test_soxx_map_takes_priority_over_extra]:
        try:
            fn(); print(f"  ✓ {fn.__name__}")
        except AssertionError as e:
            ok = False; print(f"  ✗ {fn.__name__}: {e}")
    sys.exit(0 if ok else 1)
