"""免费价格源:Yahoo(主,有复权价)+ Nasdaq(备,裸收盘)。

设计(见 docs/methodology):
- **回退**:先 Yahoo,失败自动切 Nasdaq,都失败才报错;
- **谨慎交叉校验**:两源都成功时,比较末日收盘(归一为裸 close 比),
  在容差内则记"主源=X,备源在 Y% 内吻合",背离则标红;**不夸大"一致=正确"**;
- **记录来源**:返回 meta.source,保证可复现、口径透明。

返回结构与 LLMQuant equity_historical_prices 对齐:{"ticker","prices":[{time,open,high,low,close,volume,adjusted_close}...]}
"""
from __future__ import annotations

import datetime as _dt
import json
import urllib.error
import urllib.request
from typing import Any

_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"


class PriceSourceError(RuntimeError):
    pass


def _get(url: str, timeout: int = 20) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": _UA, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read()
    except (urllib.error.HTTPError, urllib.error.URLError) as e:
        raise PriceSourceError(f"{url[:60]}...: {e}") from e


def yahoo_prices(ticker: str, start: str, end: str) -> list[dict[str, Any]]:
    """Yahoo Finance 日线,含 adjusted_close。"""
    p1 = int(_dt.datetime.strptime(start, "%Y-%m-%d").timestamp())
    p2 = int((_dt.datetime.strptime(end, "%Y-%m-%d") + _dt.timedelta(days=1)).timestamp())
    url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
           f"?period1={p1}&period2={p2}&interval=1d")
    d = json.loads(_get(url))
    res = (d.get("chart") or {}).get("result") or []
    if not res:
        raise PriceSourceError(f"Yahoo 无数据:{ticker}")
    r = res[0]
    ts = r.get("timestamp") or []
    q = (r.get("indicators", {}).get("quote") or [{}])[0]
    adj = (r.get("indicators", {}).get("adjclose") or [{}])[0].get("adjclose") or []
    out = []
    for i, t in enumerate(ts):
        c = q.get("close", [None] * len(ts))[i]
        if c is None:
            continue
        out.append({
            "time": _dt.datetime.utcfromtimestamp(t).strftime("%Y-%m-%d"),
            "open": q.get("open", [None] * len(ts))[i],
            "high": q.get("high", [None] * len(ts))[i],
            "low": q.get("low", [None] * len(ts))[i],
            "close": c,
            "volume": q.get("volume", [None] * len(ts))[i],
            "adjusted_close": adj[i] if i < len(adj) and adj[i] is not None else c,
        })
    return out


def nasdaq_prices(ticker: str, start: str, end: str) -> list[dict[str, Any]]:
    """Nasdaq 日线,仅裸收盘(adjusted_close 置为 close)。"""
    def _fmt(s):
        return _dt.datetime.strptime(s, "%Y-%m-%d").strftime("%Y-%m-%d")
    rows = None
    for ac in ("etf", "stocks"):
        url = (f"https://api.nasdaq.com/api/quote/{ticker}/historical"
               f"?assetclass={ac}&fromdate={_fmt(start)}&todate={_fmt(end)}&limit=9999")
        try:
            d = json.loads(_get(url))
        except PriceSourceError:
            continue
        rows = ((d.get("data") or {}).get("tradesTable") or {}).get("rows")
        if rows:
            break
    if not rows:
        raise PriceSourceError(f"Nasdaq 无数据:{ticker}")

    def _num(x):
        return float(str(x).replace("$", "").replace(",", "").strip())

    out = []
    for r in rows:
        c = _num(r["close"])
        out.append({
            "time": _dt.datetime.strptime(r["date"], "%m/%d/%Y").strftime("%Y-%m-%d"),
            "open": _num(r.get("open", r["close"])),
            "high": _num(r.get("high", r["close"])),
            "low": _num(r.get("low", r["close"])),
            "close": c,
            "volume": None,
            "adjusted_close": c,   # Nasdaq 无复权,置为裸收盘
        })
    out.sort(key=lambda b: b["time"])
    return out


# 源顺序:Yahoo 主(有复权价)→ Nasdaq 备
_PROVIDERS = [("yahoo", yahoo_prices), ("nasdaq", nasdaq_prices)]


def fetch_prices(ticker: str, start: str, end: str, on_progress=None, providers=None) -> dict[str, Any]:
    """回退 + 谨慎交叉校验。返回 {"ticker","prices","source","cross_check"}。

    providers:可注入 [(name, fn), ...] 用于测试;默认 [Yahoo, Nasdaq]。
    """
    got: dict[str, list] = {}
    primary = None
    for name, fn in (providers or _PROVIDERS):
        try:
            if on_progress:
                on_progress(f"价格源 {name} ...")
            rows = fn(ticker, start, end)
            if rows:
                got[name] = rows
                if primary is None:
                    primary = name
        except PriceSourceError as e:
            if on_progress:
                on_progress(f"价格源 {name} 失败:{e}")
    if primary is None:
        raise PriceSourceError(f"所有免费价格源均失败:{ticker}")

    # 交叉校验:两源都有时,比末日裸收盘(归一口径),不夸大"一致=正确"
    cross = f"仅 {primary} 可用(另一源未返回)"
    names = list(got)
    if len(names) >= 2:
        a, b = names[0], names[1]
        ea, eb = got[a][-1]["close"], got[b][-1]["close"]
        diff = abs(ea - eb) / eb * 100 if eb else 0.0
        if diff <= 0.5:
            cross = f"主源 {a};{b} 末日收盘在 {diff:.2f}% 内吻合(一致不等于正确)"
        else:
            cross = f"⚠️ 两源背离 {diff:.2f}%(主源 {a}={ea}, {b}={eb}),已如实标注"
    return {"ticker": ticker, "prices": got[primary], "source": primary, "cross_check": cross}
