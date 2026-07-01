"""HTML 导出:把 ScanResult 渲染成自包含(内联 CSS)的一页 HTML dashboard。

设计:事实表格 + 简单 CSS 条形图(集中度分档 / 13F 覆盖度);🧠 解读独立样式分区;
底部免责。无外部依赖、无 JS,可直接浏览器打开或转 PDF。数字仍来自确定性计算。
"""
from __future__ import annotations

import html

from .scan import ScanResult

_CSS = """
:root{--ink:#1a1f36;--muted:#6b7280;--line:#e5e7eb;--brand:#0b5cad;--brainbg:#f3f7ff;--brandsoft:#dbeafe}
*{box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;
 color:var(--ink);max-width:920px;margin:0 auto;padding:32px 24px;line-height:1.55;background:#fff}
h1{font-size:24px;margin:0 0 4px;border-bottom:3px solid var(--brand);padding-bottom:10px}
h2{font-size:17px;margin:28px 0 10px;color:var(--brand)}
.sub{color:var(--muted);font-size:13px;margin-bottom:20px}
table{border-collapse:collapse;width:100%;font-size:13.5px;margin:6px 0}
th,td{border:1px solid var(--line);padding:7px 10px;text-align:left;vertical-align:top}
th{background:#f9fafb;font-weight:600}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums}
.brain{background:var(--brainbg);border-left:4px solid var(--brand);padding:10px 14px;margin:8px 0;border-radius:4px;font-size:13.5px}
.brain .tag{font-weight:700;color:var(--brand)}
.bar{background:var(--brandsoft);height:16px;border-radius:3px;display:inline-block;vertical-align:middle}
.barwrap{display:flex;align-items:center;gap:8px}
.note{color:var(--muted);font-size:12.5px}
.warn{color:#b45309;font-weight:600}
.disclaimer{margin-top:32px;border-top:1px solid var(--line);padding-top:14px;color:var(--muted);font-size:12px}
.kpis{display:flex;gap:14px;flex-wrap:wrap;margin:10px 0}
.kpi{border:1px solid var(--line);border-radius:6px;padding:8px 14px;min-width:120px}
.kpi .v{font-size:20px;font-weight:700}.kpi .l{font-size:11.5px;color:var(--muted)}
"""


def _e(x) -> str:
    return html.escape(str(x if x is not None else "—"))


def _money_b(v):
    return "—" if v is None else f"${v/1e9:.2f}B"


def _agg(v):
    if v is None:
        return "—"
    for u, d in (("T", 1e12), ("B", 1e9), ("M", 1e6)):
        if abs(v) >= d:
            return f"${v/d:.2f}{u}"
    return f"${v:.0f}"


def render_html(s: ScanResult, interp=None) -> str:
    c = s.concentration
    P: list[str] = []
    P.append("<!doctype html><html lang='zh'><head><meta charset='utf-8'>")
    P.append(f"<title>Sector Smart Money Scan — {_e(s.etf)}</title><style>{_CSS}</style></head><body>")
    P.append(f"<h1>Sector Smart Money Scan — {_e(s.etf)}</h1>")
    P.append(f"<div class='sub'>{_e(s.fund_name)} · 持仓 as-of {_e(s.holdings_as_of)} · "
             f"来源 {_e(s.holdings_source)} · 覆盖 {_e(s.coverage_status)}</div>")

    # ① KPI + 速览
    P.append("<h2>① 一句话速览</h2>")
    P.append("<div class='kpis'>")
    P.append(f"<div class='kpi'><div class='v'>{c.top_n_pct:.1f}%</div><div class='l'>前{c.top_n}大集中度</div></div>")
    P.append(f"<div class='kpi'><div class='v'>{c.core_pct:.1f}%</div><div class='l'>核心{c.core_n}只</div></div>")
    P.append(f"<div class='kpi'><div class='v'>{s.price.total_return_pct:+.1f}%</div><div class='l'>窗口收益</div></div>")
    P.append(f"<div class='kpi'><div class='v'>{_money_b(s.aum)}</div><div class='l'>AUM</div></div>")
    P.append("</div>")
    P.append(f"<div class='note'>{_e(s.etf)} 前 {c.top_n} 大占 {c.top_n_pct:.1f}%,核心 {c.core_n} 只"
             f"({_e('/'.join(c.core_tickers))})占 {c.core_pct:.1f}%。</div>")
    if interp and interp.one_line:
        P.append(f"<div class='brain'><span class='tag'>🧠 解读</span> {_e(interp.one_line)}</div>")

    # ③ 集中度(带条形)
    P.append("<h2>③ 持仓集中度</h2><table><tr><th>分档</th><th class='num'>占比</th><th>占比条</th></tr>")
    for label, pct in c.as_rows():
        w = max(0.0, min(100.0, pct))
        P.append(f"<tr><td>{_e(label)}</td><td class='num'>{pct:.2f}%</td>"
                 f"<td><span class='bar' style='width:{w*3:.0f}px'></span></td></tr>")
    P.append(f"<tr><th>合计</th><th class='num'>{c.total_pct:.2f}%</th><th></th></tr></table>")
    if interp and interp.crowding_note:
        P.append(f"<div class='brain'><span class='tag'>🧠 解读</span> {_e(interp.crowding_note)}</div>")

    # ④ 矩阵(带 holder 覆盖条)
    P.append(f"<h2>④ 成分股 × 聪明钱矩阵 (Top {s.top_n})</h2>")
    P.append("<table><tr><th>#</th><th>Ticker</th><th>名称</th><th class='num'>权重</th>"
             "<th class='num'>13F持有者</th><th>覆盖度</th><th class='num'>合计13F市值</th><th>主要机构</th></tr>")
    maxhc = max((r.holder_count or 0) for r in s.matrix) or 1
    for r in s.matrix:
        hc = r.holder_count or 0
        P.append(f"<tr><td>{r.rank}</td><td>{_e(r.ticker)}</td><td>{_e(r.name)}</td>"
                 f"<td class='num'>{r.weight_pct:.2f}%</td><td class='num'>{_e(r.holder_count)}</td>"
                 f"<td><span class='bar' style='width:{hc/maxhc*90:.0f}px'></span></td>"
                 f"<td class='num'>{_agg(r.aggregate_value_usd)}</td><td>{_e(', '.join(r.top_holders))}</td></tr>")
    P.append("</table>")
    if interp and interp.quick_reads:
        P.append("<div class='brain'><span class='tag'>🧠 成分股快读</span><ul>")
        for r in s.matrix:
            qr = interp.quick_reads.get(r.ticker)
            if qr:
                P.append(f"<li><b>{_e(r.ticker)}</b> — {_e(qr)}</li>")
        P.append("</ul></div>")

    # ⑤ 重复暴露
    P.append("<h2>⑤ 重复暴露检查</h2>")
    if s.duplicate and s.duplicate.found:
        d = s.duplicate
        line = f"已持有 <b>{_e(d.ticker)}</b>,再买 {_e(s.etf)}:该股权重 <b>{d.weight_pct:.2f}%</b>。"
        if d.indirect_amount is not None:
            line += f" 每投入 ${d.invest_amount:,.0f},间接增加 {_e(d.ticker)} 暴露 <b>${d.indirect_amount:,.0f}</b>。"
        P.append(f"<p>{line}</p>")
    elif s.duplicate:
        P.append(f"<p>{_e(s.duplicate.ticker)} 不在 {_e(s.etf)} 持仓中,无直接重复暴露。</p>")
    else:
        P.append("<p class='note'>(未指定重复暴露检查标的)</p>")

    # ⑥ 价格窗口
    p = s.price
    P.append("<h2>⑥ 90 天价格窗口</h2><table>")
    P.append(f"<tr><th>窗口</th><td>{_e(p.start_date)} ~ {_e(p.end_date)}({p.n_bars} 交易日)</td></tr>")
    P.append(f"<tr><th>起始/结束收盘</th><td>{p.start_close:.2f} → {p.end_close:.2f}</td></tr>")
    P.append(f"<tr><th>区间收益</th><td>{p.total_return_pct:+.2f}%</td></tr></table>")

    # ⑦ 数据质量
    P.append("<h2>⑦ 数据质量说明</h2><ul class='note'>")
    P.append(f"<li>持仓为 SEC N-PORT 监管快照(as-of {_e(s.holdings_as_of)},coverage={_e(s.coverage_status)}),非实时日度持仓。</li>")
    P.append(f"<li>权重合计 {c.total_pct:.2f}%(含现金 {c.cash_pct:.2f}%),现金单列未混入股票集中度。</li>")
    P.append(f"<li>13F「持有者数」为 SEC Form 13F Top1000 机构内口径,ranking_period={_e(s.thirteen_f_period)}。</li>")
    P.append("<li>「合计 13F 市值」为申报时点 as-reported 市值,跨源比较可能有数个百分点差异。</li>")
    P.append(f"<li>成分股解析:{s.equity_count} 只已解析、{s.cash_count} 行现金、"
             f"<b>{s.unresolved_count} 只未解析 (UNRESOLVED)</b>。</li>")
    if s.unresolved_count:
        P.append(f"<li class='warn'>⚠️ {s.unresolved_count} 只未解析,集中度/矩阵仅覆盖已解析持仓:"
                 f"{_e(', '.join(s.unresolved_names))}。</li>")
    P.append("</ul>")

    # ⑧ 风险披露 + 免责
    P.append("<h2>⑧ 风险披露</h2>")
    P.append("<p class='note'>本页为信息研究用途,基于公开监管数据的确定性聚合,不构成投资建议。"
             "13F 为延迟披露的季度末仓位;ETF 持仓为监管快照,可能与当前实际持仓不同。</p>")
    if interp:
        P.append("<p class='note'>标 🧠 者为 AI 定性解读(不含阿拉伯数字、不参与计算),与确定性事实分区呈现。</p>")
    P.append("<div class='disclaimer'>免责声明:本报告仅供信息与研究用途,不构成投资建议、要约或买卖推荐。"
             "数据来自 SEC N-PORT / Form 13F 等延迟披露的监管文件,可能与当前实际持仓不同,历史表现不预示未来。"
             "使用后果自负。Past performance is not indicative of future results.</div>")
    P.append("</body></html>")
    return "".join(P)
