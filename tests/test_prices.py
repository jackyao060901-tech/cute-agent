"""第 3 阶验收测试:SOXX 90 天窗口收益,确定性、对账文章 +78.2%。用 fixture,0 credits。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sector_scan.scan.prices import build_price_window  # noqa: E402

FIXTURE = (
    Path(__file__).resolve().parent.parent
    / "sector_scan/fixtures/soxx_prices_2026-03-23_06-17.json"
)
ARTICLE_RETURN = 78.2  # 文章公布


def _pw():
    data = json.load(open(FIXTURE, encoding="utf-8"))
    return build_price_window("SOXX", data)


def test_window_dates_and_bars():
    pw = _pw()
    assert pw.start_date == "2026-03-23", pw.start_date
    assert pw.end_date == "2026-06-17", pw.end_date
    assert pw.n_bars == 61, pw.n_bars


def test_return_matches_article():
    pw = _pw()
    # 文章四舍五入到 78.2%,允许 0.5pct 容差
    assert abs(pw.total_return_pct - ARTICLE_RETURN) < 0.5, pw.total_return_pct
    assert abs(pw.price_return_pct - ARTICLE_RETURN) < 0.5, pw.price_return_pct


def test_return_is_deterministic():
    # 同一 fixture 多次计算必须完全一致(可复现)
    assert _pw().total_return_pct == _pw().total_return_pct


if __name__ == "__main__":
    pw = _pw()
    print(f"SOXX {pw.start_date}~{pw.end_date} ({pw.n_bars} 交易日)")
    print(f"  close {pw.start_close:.2f} -> {pw.end_close:.2f}")
    print(f"  价格涨幅 {pw.price_return_pct:+.2f}% | 总收益 {pw.total_return_pct:+.2f}% | 文章 +{ARTICLE_RETURN}%")
    ok = True
    for fn in [test_window_dates_and_bars, test_return_matches_article, test_return_is_deterministic]:
        try:
            fn(); print(f"  ✓ {fn.__name__}")
        except AssertionError as e:
            ok = False; print(f"  ✗ {fn.__name__}: {e}")
    sys.exit(0 if ok else 1)
