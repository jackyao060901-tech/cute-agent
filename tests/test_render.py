"""第 5 阶验收:渲染出的 dashboard 含全部 8 模块与关键事实。用 fixture,0 credits。"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sector_scan.scan.scan import build_scan_from_fixtures  # noqa: E402
from sector_scan.scan.render import render_dashboard  # noqa: E402


def _md():
    return render_dashboard(build_scan_from_fixtures(dup_ticker="NVDA", invest_amount=100_000))


def test_eight_modules_present():
    md = _md()
    for marker in ["① 一句话速览", "② 板块快照", "③ 持仓集中度",
                   "④ 成分股 × 聪明钱矩阵", "⑤ 重复暴露检查",
                   "⑥ 90 天价格窗口", "⑦ 数据质量说明", "⑧ 风险披露"]:
        assert marker in md, f"缺模块: {marker}"


def test_key_facts_present():
    md = _md()
    for fact in ["56.3%", "+78.2%", "779", "$2.31T", "$8,263", "$17.52B", "stale"]:
        assert fact in md, f"缺关键事实: {fact}"


def test_no_unresolved_leak():
    # 不应出现未解析占位泄漏到正文
    md = _md()
    assert "None" not in md, "渲染结果含 None,存在缺值未处理"


def test_resolution_disclosed():
    # 数据质量说明必须显式披露解析情况(含 UNRESOLVED 计数),不依赖颜色
    md = _md()
    assert "UNRESOLVED" in md and "已解析" in md
    assert "30 只股票已解析" in md and "0 只未解析" in md


def _not_covered_scan():
    """构造一个成分股全部未解析的 ETF(离线,不花额度)。"""
    from sector_scan.scan.scan import build_scan
    holdings = {"ticker": "XTEST", "fund_name": "Test Fund", "as_of_date": "2025-12-31",
                "source": "sec_nport", "coverage_status": "stale",
                "holdings": [{"holding_name": "Foo Corp", "isin": "US000000FOO0", "cusip": None,
                              "weight": 0.6, "market_value": 6},
                             {"holding_name": "Bar Inc", "isin": "US000000BAR0", "cusip": None,
                              "weight": 0.4, "market_value": 4}]}
    lookup = {"fund_name": "Test Fund", "aum": 1e9}
    prices = {"prices": [{"time": "2026-03-23", "close": 100, "adjusted_close": 100},
                         {"time": "2026-06-17", "close": 110, "adjusted_close": 110}]}
    return build_scan(holdings, lookup, {}, prices, dup_ticker=None)


def test_not_covered_graceful():
    """0 只解析时:醒目覆盖提示 + 集中度标'不适用',不把 0.0% 当事实。"""
    from sector_scan.scan.render import render_dashboard
    s = _not_covered_scan()
    assert s.equity_count == 0 and s.unresolved_count == 2
    md = render_dashboard(s)
    assert "覆盖提示" in md and "不适用" in md
    assert "占 **0.0%**" not in md  # 不得出现误导性 0.0% 集中度断言


if __name__ == "__main__":
    md = _md()
    ok = True
    for fn in [test_eight_modules_present, test_key_facts_present, test_no_unresolved_leak,
               test_resolution_disclosed, test_not_covered_graceful]:
        try:
            fn(); print(f"  ✓ {fn.__name__}")
        except AssertionError as e:
            ok = False; print(f"  ✗ {fn.__name__}: {e}")
    print(f"\ndashboard 长度 {len(md)} 字符")
    sys.exit(0 if ok else 1)
