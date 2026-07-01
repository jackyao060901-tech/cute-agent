"""命令行入口:一行生成一页 Sector Smart Money Scan。

示例:
  python -m sector_scan SOXX --hold NVDA --invest 100000
  python -m sector_scan SOXX --start 2026-03-23 --end 2026-06-17 --year 2025 --quarter 4
  python -m sector_scan --fixtures           # 离线、用内置 SOXX 快照(0 credit)
  python -m sector_scan SOXX --no-brain       # 只出确定性事实,不调 DeepSeek
"""
from __future__ import annotations

import argparse
import datetime as _dt
import sys

from .scan.render import render_dashboard


def _default_window() -> tuple[str, str]:
    end = _dt.date.today()
    start = end - _dt.timedelta(days=90)
    return start.isoformat(), end.isoformat()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="sector_scan", description="Sector Smart Money Scan")
    ap.add_argument("etf", nargs="?", default="SOXX", help="行业 ETF 代码(默认 SOXX)")
    ap.add_argument("--hold", default=None,
                    help="重复暴露检查标的(仅 SOXX 缺省为 NVDA;其他 ETF 缺省关闭;空串显式关闭)")
    ap.add_argument("--no-hold", action="store_true", help="显式关闭重复暴露检查(等价 --hold \"\")")
    ap.add_argument("--invest", type=float, default=100_000, help="投入金额,用于重复暴露估算")
    ap.add_argument("--start", help="价格窗口起(YYYY-MM-DD,默认近90天)")
    ap.add_argument("--end", help="价格窗口止(YYYY-MM-DD,默认今天)")
    ap.add_argument("--year", type=int, help="13F 年份(默认最新季)")
    ap.add_argument("--quarter", type=int, help="13F 季度 1-4(默认最新季)")
    ap.add_argument("--top", type=int, default=10, help="Top N 成分股(默认10)")
    ap.add_argument("--core", type=int, default=5, help="核心 N 只(默认5)")
    ap.add_argument("--no-brain", action="store_true", help="不调用 DeepSeek 解读层")
    ap.add_argument("--fixtures", action="store_true", help="离线:用内置 SOXX 快照(0 credit)")
    ap.add_argument("--html", action="store_true", help="输出 HTML(而非 markdown)")
    ap.add_argument("--out", help="写入文件而非标准输出")
    ap.add_argument("--pdf", help="导出 PDF 到指定路径(需本机 Chromium)")
    args = ap.parse_args(argv)

    # 重复暴露标的:--no-hold 显式关闭;否则仅 SOXX 缺省 NVDA(对标文章),其他 ETF 缺省关闭。
    if args.no_hold:
        dup = None
    elif args.hold is None:
        dup = "NVDA" if args.etf.upper() == "SOXX" else None
    else:
        dup = args.hold or None

    if args.fixtures:
        # 离线 fixture 仅覆盖 SOXX 已审计快照,拒绝用它冒充其他 ETF。
        if args.etf.upper() != "SOXX":
            print(f"[错误] --fixtures 仅支持 SOXX 已审计快照;{args.etf} 请去掉 --fixtures 走实时。",
                  file=sys.stderr)
            return 2
        from .scan.scan import build_scan_from_fixtures
        scan = build_scan_from_fixtures(dup_ticker=dup, invest_amount=args.invest)
    else:
        from .scan.scan import build_scan_live
        start = args.start or _default_window()[0]
        end = args.end or _default_window()[1]
        try:
            scan = build_scan_live(
                args.etf, start_date=start, end_date=end,
                year=args.year, quarter=args.quarter,
                dup_ticker=dup, invest_amount=args.invest,
                core_n=args.core, top_n=args.top,
                on_progress=lambda m: print(f"  · {m}", file=sys.stderr),
            )
        except Exception as e:  # noqa: BLE001 — CLI 顶层,友好报错
            print(f"[错误] 取数失败:{e}", file=sys.stderr)
            return 2

    interp = None
    if not args.no_brain:
        try:
            from .brain.interpret import interpret
            print("  · DeepSeek 解读 ...", file=sys.stderr)
            interp, reason = interpret(scan)
            if interp is None:
                print(f"  · 解读降级(仅出事实版)。原因:{reason}", file=sys.stderr)
        except Exception as e:  # noqa: BLE001
            print(f"  · 解读跳过:{e}", file=sys.stderr)

    if args.pdf:
        from .scan.render_html import render_html
        from .scan.export_pdf import html_to_pdf, PdfExportError
        try:
            html_to_pdf(render_html(scan, interp), args.pdf)
            print(f"已导出 PDF:{args.pdf}", file=sys.stderr)
        except PdfExportError as e:
            print(f"[错误] PDF 导出失败:{e}", file=sys.stderr)
            return 2
        return 0

    if args.html:
        from .scan.render_html import render_html
        output = render_html(scan, interp)
    else:
        output = render_dashboard(scan, interp)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"已写入 {args.out}", file=sys.stderr)
    else:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
