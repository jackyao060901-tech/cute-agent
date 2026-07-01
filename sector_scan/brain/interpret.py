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

# 违禁词护栏:超出"主要持有人/集中度"事实所能支撑的措辞,出现即判违规
BANNED_PHRASES = ("主导", "重仓", "控制", "控盘", "操纵", "龙头地位", "收益强劲", "涨幅领先",
                  "被动", "主动管理")  # 数据只给 top holders,不含主动/被动分类

SYSTEM = (
    "你是严谨的量化研究助理,为券商撰写半导体 ETF 的板块解读。审计友好、克制、可被表格逐句支撑。"
    "铁律:"
    "(1) 只能基于用户提供的事实写解读,绝不编造或引入任何新数据/新标的;"
    "(2) **全部输出严禁出现任何阿拉伯数字 0-9**——所有数字已在报告表格里,你只用文字描述程度"
    "(如'高度集中''机构覆盖最广');"
    "(3) **只做事实翻译,不做额外推断**,尤其:"
    "  · 不得对单只成分股的收益/涨跌下判断——报告只有 ETF 整体价格窗口收益,没有逐只个股收益;"
    "  · 'top holders/主要机构'仅表示按 13F 持仓市值最大的机构,**不得**说成'重仓''主导''控制',"
    "    也**不得**给机构贴'主动/被动/资产管理/金融机构'等数据未提供的类型描述;"
    "    描述机构时只列其名称,写'主要持有人包括…'或'位列主要持有人';"
    "  · 涉及拥挤度/机构覆盖度的比较须限定'在本页所示样本内',不得暗示全市场排名;"
    "(4) 简洁专业的中文;不做买卖建议。"
    "只输出 JSON,字段:one_line、crowding_note、quick_reads(键=ticker,值=该股一句话定性快读)。"
)


@dataclass
class Interpretation:
    one_line: str
    crowding_note: str
    quick_reads: dict[str, str]

    def _all_texts(self) -> list[str]:
        return [self.one_line, self.crowding_note, *self.quick_reads.values()]

    def has_any_digit(self) -> bool:
        return any(_DIGIT.search(t or "") for t in self._all_texts())

    def banned_phrases_found(self) -> list[str]:
        joined = " ".join(self._all_texts())
        return [w for w in BANNED_PHRASES if w in joined]


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


def interpret(
    s: ScanResult, *, model: str = "deepseek-v4-pro", max_retries: int = 3
) -> "tuple[Interpretation | None, str]":
    """调用大脑生成解读。返回 (解读或None, 原因)。

    失败/违规则返回 (None, 具体原因),CLI 据此告知用户是"网络超时"还是"护栏拦截",
    便于诊断;事实层不受影响。
    首次 temperature=0(可复现);重试时升温,让模型换措辞绕开违禁词,提高成功率。
    """
    user = _facts_text(s)
    reason = "未知"
    for attempt in range(max_retries + 1):
        temp = 0.0 if attempt == 0 else min(0.3 + 0.3 * attempt, 1.0)
        try:
            raw = chat(
                [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}],
                model=model, temperature=temp, response_json=True,
            )
        except DeepSeekError as e:
            reason = f"DeepSeek 连接/接口失败:{e}"
            continue
        try:
            data = json.loads(raw)
            interp = Interpretation(
                one_line=data.get("one_line", "").strip(),
                crowding_note=data.get("crowding_note", "").strip(),
                quick_reads={str(k).upper(): str(v).strip() for k, v in (data.get("quick_reads") or {}).items()},
            )
        except (json.JSONDecodeError, AttributeError, TypeError):
            reason = "DeepSeek 返回非预期 JSON"
            continue
        digit_bad = interp.has_any_digit()
        banned = interp.banned_phrases_found()
        if not digit_bad and not banned:   # 双护栏:数字 + 违禁词
            return interp, "ok"
        # 违规 -> 记录原因并追加更强约束重试
        parts = (["阿拉伯数字"] if digit_bad else []) + ([f"违禁词{banned}"] if banned else [])
        reason = "输出未过护栏(含 " + "、".join(parts) + ")"
        warn = "\n严重警告:上次输出违规,请重写。"
        if digit_bad:
            warn += "不得出现任何阿拉伯数字 0-9。"
        if banned:
            warn += f"不得使用这些词:{'、'.join(banned)};改用'主要持有人包括…',且不要对单只个股收益下判断。"
        user += warn
    return None, reason
