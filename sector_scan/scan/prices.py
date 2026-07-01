"""第 3 阶:价格层 —— ETF 在观察窗口内的确定性区间收益。

收益全部确定性计算,LLM 不经手。按文档建议:
- adjusted_close 已含分红/拆股,适合算"总收益";
- close 是名义收盘价,适合算"价格涨幅"。
两者都算出来,口径写清楚,避免误读。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..data import llmquant


@dataclass
class PriceWindow:
    ticker: str
    start_date: str          # 窗口内首个交易日(实际)
    end_date: str            # 窗口内末个交易日(实际)
    start_close: float
    end_close: float
    start_adj_close: float
    end_adj_close: float
    n_bars: int

    @property
    def price_return_pct(self) -> float:
        """名义价格涨幅(用 close)。"""
        return 100.0 * (self.end_close / self.start_close - 1.0)

    @property
    def total_return_pct(self) -> float:
        """总收益(用 adjusted_close,含分红/拆股)。"""
        return 100.0 * (self.end_adj_close / self.start_adj_close - 1.0)


def build_price_window(ticker: str, data: dict[str, Any]) -> PriceWindow:
    prices = data.get("prices") or []
    if not prices:
        raise ValueError(f"{ticker}: 价格窗口为空")
    # 防御:文档称按时间升序,但显式按 time 排序,避免接口顺序变动导致起止价颠倒
    prices = sorted(prices, key=lambda b: b.get("time") or "")
    first, last = prices[0], prices[-1]
    return PriceWindow(
        ticker=ticker,
        start_date=first.get("time"),
        end_date=last.get("time"),
        start_close=first.get("close"),
        end_close=last.get("close"),
        start_adj_close=first.get("adjusted_close"),
        end_adj_close=last.get("adjusted_close"),
        n_bars=len(prices),
    )


def fetch_price_window(ticker: str, start_date: str, end_date: str) -> PriceWindow:
    data = llmquant.equity_historical_prices(ticker, start_date=start_date, end_date=end_date)
    return build_price_window(ticker, data)
