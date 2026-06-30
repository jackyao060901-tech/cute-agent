"""LLMQuant Data HTTP 客户端.

只用标准库(urllib),避免引入依赖,保证哪里都能跑。后续可升级到 httpx。
每个方法返回的是接口 `data` 字段(已剥掉外层 meta),并附带 credits 信息打印。

接口签名见 docs/research/00-preparation-dossier.md 第 3 节,均已实测:
    etf_lookup            0 credits
    etf_holdings          1 credit
    sec_13f_list_ticker_holders  1 credit/票
    equity_historical_prices     0 credits
"""
from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from .. import config


class LLMQuantError(RuntimeError):
    """接口返回错误或网络失败。"""


def _get(path: str, params: dict[str, Any]) -> dict[str, Any]:
    qs = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
    url = f"{config.LLMQUANT_BASE_URL}{path}?{qs}"
    req = urllib.request.Request(
        url, headers={"Authorization": f"Bearer {config.llmquant_api_key()}"}
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        raise LLMQuantError(f"HTTP {e.code} on {path}: {body}") from e
    except urllib.error.URLError as e:
        raise LLMQuantError(f"网络失败 on {path}: {e}") from e

    if isinstance(payload, dict) and payload.get("error"):
        raise LLMQuantError(f"接口错误 on {path}: {payload['error']}")
    return payload


def etf_holdings(ticker: str, limit: int = 50, as_of: str | None = None) -> dict[str, Any]:
    """ETF 监管持仓(N-PORT 快照),按权重降序。返回 data 字段。"""
    payload = _get("/api/etf/holdings", {"ticker": ticker, "limit": limit, "as_of": as_of})
    return payload.get("data", {})


def etf_lookup(ticker: str, as_of: str | None = None) -> dict[str, Any]:
    """ETF 身份 / AUM / 概要。返回 data 字段。"""
    payload = _get("/api/etf/lookup", {"ticker": ticker, "as_of": as_of})
    return payload.get("data", {})


def sec_13f_list_ticker_holders(
    ticker: str,
    year: int | None = None,
    quarter: int | None = None,
    limit: int = 100,
) -> dict[str, Any]:
    """某只股票的 13F 机构持有者(反向 13F)。返回 data 字段。

    关键字段:total_holders_in_scope(Top1000 机构内的持有者数量)、
    aggregate_value_usd(合计持仓市值)、holders[](按市值降序,含 manager_name)。
    成本:1 credit/次。年/季省略 = 最新季度。
    """
    payload = _get(
        "/api/filings/13f/by-ticker",
        {"ticker": ticker, "year": year, "quarter": quarter, "limit": limit},
    )
    return payload.get("data", {})


def equity_historical_prices(
    ticker: str,
    start_date: str | None = None,
    end_date: str | None = None,
    limit: int | None = None,
) -> dict[str, Any]:
    """美股日线 OHLCV(含 adjusted_close)。返回 data 字段。成本:0 credits。"""
    payload = _get(
        "/api/equity/historical",
        {"ticker": ticker, "start_date": start_date, "end_date": end_date, "limit": limit},
    )
    return payload.get("data", {})
