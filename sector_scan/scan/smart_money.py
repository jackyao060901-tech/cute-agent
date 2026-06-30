"""第 2 阶:13F 机构层 —— 逐个成分股取"聪明钱"覆盖度。

对每个 ticker 调 sec_13f_list_ticker_holders,提炼三件事:
  total_holders   = 文章的 "13F Holder Count"(口径:Top1000 机构内持有者数)
  aggregate_value = 合计持仓市值
  top_holders     = 市值最大的前几家机构名

数字全部来自接口返回,LLM 不经手;ranking_period 一并记录(口径透明)。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..data import llmquant


@dataclass
class HolderStats:
    ticker: str
    ranking_period: str | None
    total_holders: int | None
    aggregate_value_usd: float | None
    top_holders: list[str] = field(default_factory=list)

    @classmethod
    def from_api(cls, ticker: str, data: dict[str, Any], top_n: int = 3) -> "HolderStats":
        holders = data.get("holders") or []
        names = [h.get("manager_name") for h in holders[:top_n] if h.get("manager_name")]
        return cls(
            ticker=ticker,
            ranking_period=data.get("ranking_period"),
            total_holders=data.get("total_holders_in_scope"),
            aggregate_value_usd=data.get("aggregate_value_usd"),
            top_holders=names,
        )


def fetch_ticker_13f(
    ticker: str,
    year: int | None = None,
    quarter: int | None = None,
    top_n_holders: int = 3,
    limit: int = 100,
) -> HolderStats:
    data = llmquant.sec_13f_list_ticker_holders(ticker, year=year, quarter=quarter, limit=limit)
    return HolderStats.from_api(ticker, data, top_n=top_n_holders)


def fetch_many(
    tickers: list[str],
    year: int | None = None,
    quarter: int | None = None,
    top_n_holders: int = 3,
) -> list[HolderStats]:
    """按顺序逐个拉取(每个 1 credit)。返回与输入同序的结果。"""
    return [
        fetch_ticker_13f(t, year=year, quarter=quarter, top_n_holders=top_n_holders)
        for t in tickers
    ]
