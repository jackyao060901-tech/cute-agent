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


if __name__ == "__main__":
    md = _md()
    ok = True
    for fn in [test_eight_modules_present, test_key_facts_present, test_no_unresolved_leak,
               test_resolution_disclosed]:
        try:
            fn(); print(f"  ✓ {fn.__name__}")
        except AssertionError as e:
            ok = False; print(f"  ✗ {fn.__name__}: {e}")
    print(f"\ndashboard 长度 {len(md)} 字符")
    sys.exit(0 if ok else 1)
