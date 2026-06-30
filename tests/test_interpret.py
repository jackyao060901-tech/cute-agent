"""第 6 阶验收:解读层护栏。不调用 API,用 fixture + 构造对象验证数字护栏。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sector_scan.brain.interpret import Interpretation  # noqa: E402

FIXTURE = (
    Path(__file__).resolve().parent.parent
    / "sector_scan/fixtures/soxx_interpretation.json"
)


def test_digit_guard_detects_digit():
    bad = Interpretation("集中度56%", "ok", {"NVDA": "权重8.3%"})
    assert bad.has_any_digit() is True


def test_digit_guard_passes_clean():
    good = Interpretation("高度集中", "拥挤度居前", {"NVDA": "权重居首"})
    assert good.has_any_digit() is False


def test_banned_phrase_guard():
    bad = Interpretation("贝莱德主导该股", "ok", {"NVDA": "机构重仓"})
    assert set(bad.banned_phrases_found()) >= {"主导", "重仓"}
    good = Interpretation("机构覆盖广泛", "主要持有人包括三大资管", {"NVDA": "权重最高"})
    assert good.banned_phrases_found() == []


def test_saved_interpretation_clean():
    """已存的真实大脑输出必须零阿拉伯数字、零违禁词(防回归引入越界措辞)。"""
    d = json.load(open(FIXTURE, encoding="utf-8"))
    interp = Interpretation(d["one_line"], d["crowding_note"], d["quick_reads"])
    assert not interp.has_any_digit(), "存档解读含阿拉伯数字,违反护栏"
    assert interp.banned_phrases_found() == [], f"存档解读含违禁词: {interp.banned_phrases_found()}"
    assert interp.one_line and interp.crowding_note and interp.quick_reads


if __name__ == "__main__":
    ok = True
    for fn in [test_digit_guard_detects_digit, test_digit_guard_passes_clean,
               test_banned_phrase_guard, test_saved_interpretation_clean]:
        try:
            fn(); print(f"  ✓ {fn.__name__}")
        except AssertionError as e:
            ok = False; print(f"  ✗ {fn.__name__}: {e}")
    sys.exit(0 if ok else 1)
