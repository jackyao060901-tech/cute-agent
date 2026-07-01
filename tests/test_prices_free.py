"""免费价格 provider 测试:回退 + 交叉校验。多用例、注入假 provider,离线不联网。"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sector_scan.data.prices_free import fetch_prices, PriceSourceError  # noqa: E402


def _rows(close):
    return [{"time": "2026-06-16", "close": close - 1, "adjusted_close": close - 1},
            {"time": "2026-06-17", "close": close, "adjusted_close": close}]


def _ok(close):
    return lambda t, s, e: _rows(close)


def _fail(t, s, e):
    raise PriceSourceError("boom")


def test_fallback_when_primary_fails():
    # 主源失败 → 自动用备源
    r = fetch_prices("SOXX", "2026-03-23", "2026-06-17",
                     providers=[("yahoo", _fail), ("nasdaq", _ok(100.0))])
    assert r["source"] == "nasdaq" and r["prices"][-1]["close"] == 100.0


def test_primary_preferred_when_both_ok():
    r = fetch_prices("SOXX", "2026-03-23", "2026-06-17",
                     providers=[("yahoo", _ok(599.73)), ("nasdaq", _ok(599.73))])
    assert r["source"] == "yahoo"


def test_all_sources_fail_raises():
    try:
        fetch_prices("SOXX", "2026-03-23", "2026-06-17",
                     providers=[("yahoo", _fail), ("nasdaq", _fail)])
        assert False, "应抛错"
    except PriceSourceError:
        pass


def test_cross_check_agree():
    r = fetch_prices("SOXX", "2026-03-23", "2026-06-17",
                     providers=[("yahoo", _ok(599.73)), ("nasdaq", _ok(599.70))])
    assert "吻合" in r["cross_check"] and "背离" not in r["cross_check"]


def test_cross_check_diverge_flagged():
    # 差异 > 0.5% 应标红背离
    r = fetch_prices("SOXX", "2026-03-23", "2026-06-17",
                     providers=[("yahoo", _ok(600.0)), ("nasdaq", _ok(500.0))])
    assert "背离" in r["cross_check"]


def test_single_source_note():
    r = fetch_prices("SOXX", "2026-03-23", "2026-06-17",
                     providers=[("yahoo", _ok(599.73)), ("nasdaq", _fail)])
    assert "仅 yahoo" in r["cross_check"]


if __name__ == "__main__":
    ok = True
    for fn in [test_fallback_when_primary_fails, test_primary_preferred_when_both_ok,
               test_all_sources_fail_raises, test_cross_check_agree,
               test_cross_check_diverge_flagged, test_single_source_note]:
        try:
            fn(); print(f"  ✓ {fn.__name__}")
        except AssertionError as e:
            ok = False; print(f"  ✗ {fn.__name__}: {e}")
    sys.exit(0 if ok else 1)
