"""第 4 阶:计算层 —— 集中度分层 + 重复暴露,全部确定性计算。

口径(比文章更严谨):权重用原始值(总和 ≈102%,因含现金),
现金单独成档,不并入"其余",每一分都交代清楚。
"""
from __future__ import annotations

from dataclasses import dataclass

from ..resolve.resolver import Kind, ResolveResult


@dataclass
class ConcentrationTiers:
    core_n: int                  # "拥挤核心"取前几名(文章=5)
    top_n: int                   # 前 N 大(文章=10)
    core_tickers: list[str]
    core_pct: float              # 拥挤核心合计(前 core_n)
    other_top_pct: float         # 前 top_n 里除去核心的部分
    top_n_pct: float             # 前 top_n 合计 = core + other_top
    other_equity_pct: float      # 其余股票(top_n 之后)
    cash_pct: float              # 现金 / 货基
    excluded_pct: float          # 剔除/未解析的占位行(通常≈0,纳入对账)
    total_pct: float             # 全部(应≈102%)

    def as_rows(self) -> list[tuple[str, float]]:
        """给渲染层用的分档明细(顺序固定)。"""
        return [
            (f"拥挤核心 (Top{self.core_n}: {'/'.join(self.core_tickers)})", self.core_pct),
            (f"其他前{self.top_n}大", self.other_top_pct),
            (f"其余股票 (第{self.top_n+1}名起)", self.other_equity_pct),
            ("现金及等价物", self.cash_pct),
        ]


def concentration(res: ResolveResult, core_n: int = 5, top_n: int = 10) -> ConcentrationTiers:
    eq = res.equities  # 已按权重降序
    core = eq[:core_n]
    top = eq[:top_n]
    core_pct = 100.0 * sum(h.weight for h in core)
    top_pct = 100.0 * sum(h.weight for h in top)
    other_equity_pct = 100.0 * sum(h.weight for h in eq[top_n:])
    cash_pct = 100.0 * res.weight_sum(Kind.CASH)
    excluded_pct = 100.0 * (res.weight_sum(Kind.EXCLUDED) + res.weight_sum(Kind.UNRESOLVED))
    total_pct = 100.0 * res.weight_sum()
    return ConcentrationTiers(
        core_n=core_n,
        top_n=top_n,
        core_tickers=[h.ticker for h in core if h.ticker],
        core_pct=core_pct,
        other_top_pct=top_pct - core_pct,
        top_n_pct=top_pct,
        other_equity_pct=other_equity_pct,
        cash_pct=cash_pct,
        excluded_pct=excluded_pct,
        total_pct=total_pct,
    )


@dataclass
class DuplicateExposure:
    ticker: str
    in_etf: bool
    weight_pct: float            # 该票在 ETF 中的权重
    invest_amount: float | None  # 投入金额(可选)
    indirect_amount: float | None  # 间接增加的该票暴露金额

    @property
    def found(self) -> bool:
        return self.in_etf


def duplicate_exposure(
    res: ResolveResult, ticker: str, invest_amount: float | None = None
) -> DuplicateExposure:
    """若已持有 `ticker`,再买该 ETF 会间接增加多少 `ticker` 暴露。

    indirect_amount = weight(ticker in ETF) × 投入金额。文章只定性提示,这里给真实数字。
    """
    ticker = ticker.upper()
    match = next((h for h in res.equities if h.ticker == ticker), None)
    if match is None:
        return DuplicateExposure(ticker, False, 0.0, invest_amount, None)
    weight = match.weight
    indirect = (invest_amount * weight) if invest_amount is not None else None
    return DuplicateExposure(
        ticker=ticker,
        in_etf=True,
        weight_pct=100.0 * weight,
        invest_amount=invest_amount,
        indirect_amount=indirect,
    )
