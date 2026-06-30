"""解读层:把确定性事实交给 DeepSeek 写定性中文解读,并用硬护栏杜绝数字幻觉。

护栏:
  1) 输出只允许定性文字,**禁止任何阿拉伯数字 0-9**(数字只能在确定性表格里)。
  2) 只能基于传入事实解读,不得引入新事实/新标的。
  3) 违规则重试一次;仍违规则降级(返回 None,dashboard 仍可只凭事实出)。
事实 -> 解读单向流动;解读绝不回写数字。
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass

from .deepseek import chat, DeepSeekError
from ..scan.scan import ScanResult

_DIGIT = re.compile(r"\d")

SYSTEM = (
    "你是严谨的量化研究助理,为券商撰写半导体 ETF 的板块解读。"
    "铁律:(1) 只能基于用户提供的事实写解读,绝不编造或引入任何新数据/新标的;"
    "(2) **你的全部输出严禁出现任何阿拉伯数字 0-9**——所有数字已在报告表格里,"
    "你只用文字描述程度与含义(如'高度集中''机构覆盖最广''拥挤度居前');"
    "(3) 用简洁专业的中文;(4) 不做买卖建议。"
    "只输出 JSON,字段:one_line(一句话定性判断)、crowding_note(集中度与拥挤度的一句话解读)、"
    "quick_reads(对象:键为 ticker,值为该股一句话定性快读)。"
)


@dataclass
class Interpretation:
    one_line: str
    crowding_note: str
    quick_reads: dict[str, str]

    def has_any_digit(self) -> bool:
        texts = [self.one_line, self.crowding_note, *self.quick_reads.values()]
        return any(_DIGIT.search(t or "") for t in texts)


def _facts_text(s: ScanResult) -> str:
    c = s.concentration
    lines = [
        f"ETF: {s.etf}({s.fund_name}),半导体行业 ETF。",
        f"前{c.top_n}大集中度={c.top_n_pct:.1f}%,核心{c.core_n}只={'/'.join(c.core_tickers)}"
        f"(占{c.core_pct:.1f}%);现金占比{c.cash_pct:.1f}%;过去窗口收益{s.price.total_return_pct:+.1f}%。",
        "成分股(按权重,含13F机构覆盖度):",
    ]
    for r in s.matrix:
        lines.append(
            f"- {r.ticker} {r.name}: 权重{r.weight_pct:.1f}%, 13F持有者{r.holder_count}, "
            f"主要机构 {', '.join(r.top_holders[:3])}"
        )
    if s.duplicate and s.duplicate.found:
        lines.append(f"重复暴露: 已持有{s.duplicate.ticker}者再买本ETF会间接增加其暴露(权重{s.duplicate.weight_pct:.1f}%)。")
    lines.append("请只输出定性解读,严禁任何阿拉伯数字。")
    return "\n".join(lines)


def interpret(s: ScanResult, *, model: str = "deepseek-v4-pro", max_retries: int = 1) -> Interpretation | None:
    """调用大脑生成解读;失败或违规则返回 None(降级,事实层不受影响)。"""
    user = _facts_text(s)
    for attempt in range(max_retries + 1):
        try:
            raw = chat(
                [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}],
                model=model, temperature=0.0, response_json=True,
            )
            data = json.loads(raw)
            interp = Interpretation(
                one_line=data.get("one_line", "").strip(),
                crowding_note=data.get("crowding_note", "").strip(),
                quick_reads={k: str(v).strip() for k, v in (data.get("quick_reads") or {}).items()},
            )
        except (DeepSeekError, json.JSONDecodeError, AttributeError):
            continue
        if not interp.has_any_digit():   # 护栏:输出含数字即判违规
            return interp
        # 含数字 -> 追加更强约束重试
        user += "\n严重警告:上次输出含阿拉伯数字,违规。请重写,绝对不要出现任何 0-9。"
    return None
