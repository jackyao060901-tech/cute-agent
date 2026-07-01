"""第 7 阶验收:CLI 离线模式可跑、产出 8 模块。0 credit、不调 API。"""
from __future__ import annotations

import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sector_scan.cli import main  # noqa: E402


def _run(args):
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = main(args)
    return rc, buf.getvalue()


def test_cli_fixtures_offline():
    rc, out = _run(["--fixtures", "--no-brain"])
    assert rc == 0
    for marker in ["① 一句话速览", "② 板块快照", "③ 持仓集中度",
                   "④ 成分股 × 聪明钱矩阵", "⑤ 重复暴露检查",
                   "⑥ 90 天价格窗口", "⑦ 数据质量说明", "⑧ 风险披露"]:
        assert marker in out, f"CLI 输出缺模块: {marker}"
    assert "56.3%" in out and "+78.2%" in out


def test_fixtures_rejects_non_soxx():
    """--fixtures 只支持 SOXX,不得用 SOXX 快照冒充其他 ETF。"""
    rc, _ = _run(["XLK", "--fixtures", "--no-brain"])
    assert rc == 2


def test_soxx_default_checks_nvda_duplicate():
    """SOXX 缺省应做 NVDA 重复暴露检查(对标文章)。"""
    _, out = _run(["--fixtures", "--no-brain"])
    assert "NVDA" in out and "$8,263" in out


def test_lowercase_soxx_fixtures_accepted():
    """小写 soxx --fixtures 应被接受(大小写无关)。"""
    rc, out = _run(["soxx", "--fixtures", "--no-brain"])
    assert rc == 0 and "iShares Semiconductor ETF" in out


def test_no_hold_disables_duplicate():
    """--no-hold 应关闭重复暴露检查。"""
    rc, out = _run(["--fixtures", "--no-brain", "--no-hold"])
    assert rc == 0 and "$8,263" not in out


if __name__ == "__main__":
    ok = True
    for fn in [test_cli_fixtures_offline, test_fixtures_rejects_non_soxx,
               test_soxx_default_checks_nvda_duplicate,
               test_lowercase_soxx_fixtures_accepted, test_no_hold_disables_duplicate]:
        try:
            fn(); print(f"  ✓ {fn.__name__}")
        except AssertionError as e:
            ok = False; print(f"  ✗ {fn.__name__}: {e}")
    sys.exit(0 if ok else 1)
