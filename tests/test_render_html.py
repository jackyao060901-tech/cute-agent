"""第 8 阶验收:HTML 导出结构完整、含 8 模块与关键事实、含免责。用 fixture,0 credits。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sector_scan.scan.scan import build_scan_from_fixtures  # noqa: E402
from sector_scan.scan.render_html import render_html  # noqa: E402
from sector_scan.brain.interpret import Interpretation  # noqa: E402

FIX = Path(__file__).resolve().parent.parent / "sector_scan/fixtures/soxx_interpretation.json"


def _html(with_brain=True):
    s = build_scan_from_fixtures()
    interp = None
    if with_brain:
        d = json.load(open(FIX, encoding="utf-8"))
        interp = Interpretation(d["one_line"], d["crowding_note"], d["quick_reads"])
    return render_html(s, interp)


def test_valid_html_structure():
    h = _html()
    assert h.startswith("<!doctype html>")
    assert h.count("<html") == 1 and h.count("</html>") == 1


def test_modules_and_facts():
    h = _html()
    for m in ["① 一句话速览", "③ 持仓集中度", "④ 成分股", "⑤ 重复暴露",
              "⑥ 90 天", "⑦ 数据质量", "⑧ 风险披露"]:
        assert m in h, m
    for f in ["56.3%", "+78.2%", "779", "$8,263", "$17.52B", "免责声明"]:
        assert f in h, f


def test_brain_optional():
    assert "🧠" in _html(with_brain=True)
    assert "🧠" not in _html(with_brain=False)  # 无解读时不应出现解读块


if __name__ == "__main__":
    ok = True
    for fn in [test_valid_html_structure, test_modules_and_facts, test_brain_optional]:
        try:
            fn(); print(f"  ✓ {fn.__name__}")
        except AssertionError as e:
            ok = False; print(f"  ✗ {fn.__name__}: {e}")
    sys.exit(0 if ok else 1)
