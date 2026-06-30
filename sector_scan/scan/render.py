"""第 5 阶:渲染层 —— 把 ScanResult 渲染成 8 模块中文 markdown dashboard。

只放事实(确定性计算 + 接口数据)。解读性文字(One-Line 解读、Quick Read)
在第 6 阶由 DeepSeek 大脑补充,且与事实视觉分区。
"""
from __future__ import annotations

from .scan import ScanResult


def _money_b(v: float | None) -> str:
    if v is None:
        return "—"
    return f"${v/1e9:.2f}B"


def _agg(v: float | None) -> str:
    if v is None:
        return "—"
    for u, d in (("T", 1e12), ("B", 1e9), ("M", 1e6)):
        if abs(v) >= d:
            return f"${v/d:.2f}{u}"
    return f"${v:.0f}"


def _usd(v: float | None) -> str:
    return "—" if v is None else f"${v:,.0f}"


def render_dashboard(s: ScanResult, interp=None) -> str:
    """渲染 8 模块中文 dashboard。

    interp(可选):DeepSeek 解读对象(one_line/crowding_note/quick_reads)。
    解读全部放进「🧠 解读」标注块,与事实视觉隔离;为 None 时退化为纯事实版。
    """
    c = s.concentration
    L: list[str] = []

    L.append(f"# Sector Smart Money Scan — {s.etf}")
    L.append("")

    # ① 一句话速览(事实版;解读单列)
    L.append("## ① 一句话速览")
    L.append(
        f"**{s.etf}**({s.fund_name})前 {c.top_n} 大持仓占 **{c.top_n_pct:.1f}%**,"
        f"其中核心 {c.core_n} 只({'/'.join(c.core_tickers)})占 **{c.core_pct:.1f}%**;"
        f"过去 90 天 **{s.price.total_return_pct:+.1f}%**。"
    )
    if interp and interp.one_line:
        L.append(f"> 🧠 **解读**:{interp.one_line}")
    L.append("")

    # ② 板块快照
    L.append("## ② 板块快照 (Sector Snapshot)")
    L.append("| 字段 | 值 |")
    L.append("|---|---|")
    L.append(f"| ETF | {s.etf} |")
    L.append(f"| 基金名称 | {s.fund_name or '—'} |")
    L.append(f"| 发行方 | {s.issuer or '—'} |")
    L.append(f"| AUM | {_money_b(s.aum)} |")
    L.append(f"| 持仓来源 | {s.holdings_source or '—'} |")
    L.append(f"| 持仓日期 (as-of) | {s.holdings_as_of or '—'} |")
    L.append(f"| 覆盖状态 | {s.coverage_status or '—'} |")
    L.append(f"| 持仓结构 | {s.equity_count} 股票 + {s.cash_count} 现金行 |")
    L.append(f"| 前 {c.top_n} 大集中度 | {c.top_n_pct:.1f}% |")
    L.append(f"| 90 天收益 | {s.price.total_return_pct:+.1f}% |")
    L.append("")

    # ③ 持仓集中度
    L.append("## ③ 持仓集中度 (Holdings Concentration)")
    L.append("| 分档 | 占比 |")
    L.append("|---|---|")
    for label, pct in c.as_rows():
        L.append(f"| {label} | {pct:.2f}% |")
    L.append(f"| **合计** | **{c.total_pct:.2f}%** |")
    if interp and interp.crowding_note:
        L.append("")
        L.append(f"> 🧠 **解读**:{interp.crowding_note}")
    L.append("")

    # ④ 成分股 × 聪明钱矩阵
    L.append(f"## ④ 成分股 × 聪明钱矩阵 (Top {s.top_n})")
    L.append("| # | Ticker | 名称 | 权重 | 13F持有者数 | 合计13F市值 | 主要机构 |")
    L.append("|---|---|---|---|---|---|---|")
    for r in s.matrix:
        L.append(
            f"| {r.rank} | {r.ticker} | {r.name} | {r.weight_pct:.2f}% | "
            f"{r.holder_count if r.holder_count is not None else '—'} | "
            f"{_agg(r.aggregate_value_usd)} | {', '.join(r.top_holders) or '—'} |"
        )
    L.append("")
    if interp and interp.quick_reads:
        L.append("**🧠 成分股快读(DeepSeek 解读,非数据):**")
        for r in s.matrix:
            qr = interp.quick_reads.get(r.ticker)
            if qr:
                L.append(f"- **{r.ticker}** — {qr}")
        L.append("")

    # ⑤ 重复暴露检查
    L.append("## ⑤ 重复暴露检查 (Duplicate Exposure Check)")
    if s.duplicate and s.duplicate.found:
        d = s.duplicate
        line = (f"已持有 **{d.ticker}** 时,再买 {s.etf}:{d.ticker} 在 {s.etf} 中权重 "
                f"**{d.weight_pct:.2f}%**。")
        if d.indirect_amount is not None:
            line += f"每投入 {_usd(d.invest_amount)},间接增加 {d.ticker} 暴露 **{_usd(d.indirect_amount)}**。"
        L.append(line)
    elif s.duplicate:
        L.append(f"**{s.duplicate.ticker}** 不在 {s.etf} 持仓中,无直接重复暴露。")
    else:
        L.append("(未指定重复暴露检查标的)")
    L.append("")

    # ⑥ 90 天价格窗口
    L.append("## ⑥ 90 天价格窗口 (90-Day Price Window)")
    p = s.price
    L.append("| 字段 | 值 |")
    L.append("|---|---|")
    L.append(f"| 窗口 | {p.start_date} ~ {p.end_date}({p.n_bars} 交易日) |")
    L.append(f"| 起始收盘 | {p.start_close:.2f} |")
    L.append(f"| 结束收盘 | {p.end_close:.2f} |")
    L.append(f"| 区间收益 | {p.total_return_pct:+.2f}% |")
    L.append("")

    # ⑦ 数据质量说明
    L.append("## ⑦ 数据质量说明 (Data Quality Notes)")
    L.append(f"- 持仓为 SEC N-PORT 监管快照(as-of {s.holdings_as_of},coverage={s.coverage_status}),"
             f"**非实时日度持仓**。")
    L.append(f"- 权重合计 {c.total_pct:.2f}%(含现金/货基 {c.cash_pct:.2f}%),现金已单列,未混入股票集中度。")
    L.append(f"- 13F「持有者数」口径:SEC Form 13F **Top 1000 机构内**的持有者数量(非全市场),"
             f"ranking_period={s.thirteen_f_period}。")
    L.append("- 「合计 13F 市值」为申报时点 as-reported 全量市值;与第三方公布值可能有约 0.9–6.7% 差异"
             "(**假设**:或因估值基准不同,如更晚的市价重估)。我方不为对齐而改写接口值。")
    L.append("- 成分股 ticker 由人工核对映射表解析(已通过外部模型复核),解析不上者标红、绝不臆测。")
    L.append("")

    # ⑧ 风险披露
    L.append("## ⑧ 风险披露 (Risk Disclosure)")
    L.append("本页为信息研究用途,基于公开监管数据的确定性聚合,**不构成投资建议**。"
             "13F 为延迟披露的季度末仓位;ETF 持仓为监管快照,可能与当前实际持仓不同。")
    if interp:
        L.append("")
        L.append("> 注:标 🧠 的为 DeepSeek 大脑生成的**定性解读**(不含数字、不参与计算),"
                 "与上方确定性事实/数据分区呈现。所有数字均来自接口的确定性计算。")
    L.append("")

    return "\n".join(L)
