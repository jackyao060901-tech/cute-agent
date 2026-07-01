"""第 7 阶验收:CLI 离线模式可跑、产出 8 模块。0 credit、不调 API。"""
from __future__ import annotations

import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sector_scan.cli import main  # noqa: E402


def test_cli_fixtures_offline():
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = main(["--fixtures", "--no-brain"])
    out = buf.getvalue()
    assert rc == 0
    for marker in ["① 一句话速览", "② 板块快照", "③ 持仓集中度",
                   "④ 成分股 × 聪明钱矩阵", "⑤ 重复暴露检查",
                   "⑥ 90 天价格窗口", "⑦ 数据质量说明", "⑧ 风险披露"]:
        assert marker in out, f"CLI 输出缺模块: {marker}"
    assert "56.3%" in out and "+78.2%" in out


if __name__ == "__main__":
    try:
        test_cli_fixtures_offline()
        print("  ✓ test_cli_fixtures_offline")
    except AssertionError as e:
        print(f"  ✗ {e}"); sys.exit(1)
