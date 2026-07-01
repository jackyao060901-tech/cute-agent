"""标的解析器:把原始持仓行映射成带 ticker 与分类的结构化结果。

设计要点(对应 CLAUDE.md 铁律):
- 零运行时猜测:命中映射表才给 ticker;命中不了就标 UNRESOLVED,绝不编。
- 分类清晰:EQUITY / CASH / EXCLUDED / UNRESOLVED,便于"现金与股票仓分离"。
- 纯计算、可单测、不花 credits。
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .soxx_map import CASH_NAME_HINTS, SOXX_ISIN_MAP
from .overrides import OVERRIDE_ISIN_MAP
from .openfigi import _bad_ticker

# 人工核对映射合集(SOXX 专表 + 外资/ADR override),优先级高于 OpenFIGI
CURATED_ISIN_MAP = {**SOXX_ISIN_MAP, **OVERRIDE_ISIN_MAP}


class Kind(str, Enum):
    EQUITY = "equity"        # 正常股票,有 ticker
    CASH = "cash"            # 现金 / 货币基金,不查 13F
    EXCLUDED = "excluded"    # 占位 / 空行,剔除
    UNRESOLVED = "unresolved"  # 映射不上 —— 必须人工补表,绝不猜


@dataclass
class ResolvedHolding:
    name: str | None
    ticker: str | None
    kind: Kind
    weight: float          # 原始权重(小数,0.083 = 8.3%)
    isin: str | None
    cusip: str | None
    market_value: float | None

    @property
    def weight_pct(self) -> float:
        return 100.0 * self.weight


# 明确的占位/空行名称(非现金货基,纯占位)
PLACEHOLDER_NAMES = {"", "-", "n/a", "na", "none"}


def _looks_like_cash(name: str | None) -> bool:
    if not name:
        return False
    low = name.lower()
    return any(h in low for h in CASH_NAME_HINTS)


def _is_placeholder(name: str | None) -> bool:
    return (name or "").strip().lower() in PLACEHOLDER_NAMES


def _from_extra(extra_map, isin, cusip):
    """从外部映射(如 OpenFIGI 结果)按 isin 优先、cusip 兜底取 (ticker, kind_str)。"""
    if not extra_map:
        return None
    for key in (isin, cusip):
        if key and key in extra_map and extra_map[key]:
            return extra_map[key]
    return None


def resolve_one(raw: dict[str, Any], extra_map: dict | None = None) -> ResolvedHolding:
    name = raw.get("holding_name")
    isin = raw.get("isin")
    cusip = raw.get("cusip")
    weight = raw.get("weight") or 0.0
    mv = raw.get("market_value")

    extra = _from_extra(extra_map, isin, cusip)

    # 占位 / 空行:无任何标识符,且名称为空或为占位符(N/A 等)
    if not isin and not cusip and _is_placeholder(name):
        kind, ticker = Kind.EXCLUDED, None
    elif isin and isin in CURATED_ISIN_MAP:              # 1) 人工核对映射表(SOXX+override,最可信)
        ticker, kind_str = CURATED_ISIN_MAP[isin]
        kind = Kind.CASH if kind_str == "cash" else Kind.EQUITY
    elif extra and not (extra[1] == "equity" and _bad_ticker(extra[0])):  # 2) 外部映射(OpenFIGI),坏 ticker 拒
        ticker, kind_str = extra
        kind = Kind.CASH if kind_str == "cash" else Kind.EQUITY
    elif _looks_like_cash(name):                         # 3) 现金名称启发
        kind, ticker = Kind.CASH, None
    else:                                                # 4) 映射不上 —— 标红,绝不猜测
        kind, ticker = Kind.UNRESOLVED, None

    return ResolvedHolding(
        name=name, ticker=ticker, kind=kind, weight=weight,
        isin=isin, cusip=cusip, market_value=mv,
    )


@dataclass
class ResolveResult:
    holdings: list[ResolvedHolding]

    @property
    def equities(self) -> list[ResolvedHolding]:
        eq = [h for h in self.holdings if h.kind is Kind.EQUITY]
        return sorted(eq, key=lambda h: h.weight, reverse=True)

    @property
    def cash(self) -> list[ResolvedHolding]:
        return [h for h in self.holdings if h.kind is Kind.CASH]

    @property
    def unresolved(self) -> list[ResolvedHolding]:
        return [h for h in self.holdings if h.kind is Kind.UNRESOLVED]

    def weight_sum(self, kind: Kind | None = None) -> float:
        rows = self.holdings if kind is None else [h for h in self.holdings if h.kind is kind]
        return sum(h.weight for h in rows)

    def top_n_tickers(self, n: int = 10) -> list[str]:
        return [h.ticker for h in self.equities[:n] if h.ticker]


def resolve_holdings(raw_holdings: list[dict[str, Any]], extra_map: dict | None = None) -> ResolveResult:
    return ResolveResult([resolve_one(h, extra_map) for h in raw_holdings])
