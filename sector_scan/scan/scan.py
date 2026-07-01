"""第 5 阶:编排器 —— 把五层事实组装成 ScanResult(只放事实,不含解读)。

设计:build_scan() 接收各层原始数据(dict),做纯组装,便于用 fixture 复测;
live/fixture 两个入口分别喂真实接口或本地快照。解读(One-Line/Quick Read)
留给第 6 阶 DeepSeek 大脑,这里只产出确定性事实。
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..resolve.resolver import resolve_holdings, ResolveResult
from .compute import ConcentrationTiers, DuplicateExposure, concentration, duplicate_exposure
from .prices import PriceWindow, build_price_window
from .smart_money import HolderStats

_FIX = Path(__file__).resolve().parent.parent / "fixtures"


@dataclass
class MatrixRow:
    rank: int
    ticker: str
    name: str
    weight_pct: float
    holder_count: int | None
    aggregate_value_usd: float | None
    top_holders: list[str]


@dataclass
class ScanResult:
    # —— 板块快照 ——
    etf: str
    fund_name: str | None
    issuer: str | None
    aum: float | None
    holdings_as_of: str | None
    holdings_source: str | None
    coverage_status: str | None
    holdings_count_total: int          # 接口返回的持仓行数
    equity_count: int
    cash_count: int
    unresolved_count: int              # 未解析成分股数(必须显式披露,不可静默丢弃)
    unresolved_names: list[str]        # 未解析成分股名称
    # —— 各层结果 ——
    concentration: ConcentrationTiers
    matrix: list[MatrixRow]
    duplicate: DuplicateExposure | None
    price: PriceWindow
    thirteen_f_period: str | None
    # —— 参数 ——
    top_n: int = 10
    core_n: int = 5
    dup_ticker: str | None = None
    invest_amount: float | None = None


def build_scan(
    holdings_data: dict[str, Any],
    lookup_data: dict[str, Any],
    thirteen_f_raw: dict[str, dict[str, Any]],
    prices_data: dict[str, Any],
    *,
    dup_ticker: str | None = "NVDA",
    invest_amount: float | None = 100_000,
    core_n: int = 5,
    top_n: int = 10,
    extra_map: dict | None = None,
) -> ScanResult:
    res: ResolveResult = resolve_holdings(holdings_data.get("holdings", []), extra_map)
    conc = concentration(res, core_n=core_n, top_n=top_n)
    dup = duplicate_exposure(res, dup_ticker, invest_amount) if dup_ticker else None
    price = build_price_window(holdings_data.get("ticker", "ETF"), prices_data)

    # 组装 成分股×聪明钱 矩阵(Top N 股票 join 13F)
    matrix: list[MatrixRow] = []
    period = None
    for i, h in enumerate(res.equities[:top_n], 1):
        raw = thirteen_f_raw.get(h.ticker or "")
        hs = HolderStats.from_api(h.ticker, raw) if raw else None
        if hs and hs.ranking_period:
            period = hs.ranking_period
        matrix.append(MatrixRow(
            rank=i, ticker=h.ticker, name=h.name, weight_pct=h.weight_pct,
            holder_count=hs.total_holders if hs else None,
            aggregate_value_usd=hs.aggregate_value_usd if hs else None,
            top_holders=hs.top_holders if hs else [],
        ))

    return ScanResult(
        etf=holdings_data.get("ticker", "ETF"),
        fund_name=lookup_data.get("fund_name") or holdings_data.get("fund_name"),
        issuer=lookup_data.get("issuer"),
        aum=lookup_data.get("aum"),
        holdings_as_of=holdings_data.get("as_of_date"),
        holdings_source=holdings_data.get("source"),
        coverage_status=holdings_data.get("coverage_status"),
        holdings_count_total=len(holdings_data.get("holdings", [])),
        equity_count=len(res.equities),
        cash_count=len(res.cash),
        unresolved_count=len(res.unresolved),
        unresolved_names=[h.name for h in res.unresolved],
        concentration=conc,
        matrix=matrix,
        duplicate=dup,
        price=price,
        thirteen_f_period=period,
        top_n=top_n, core_n=core_n,
        dup_ticker=dup_ticker, invest_amount=invest_amount,
    )


def build_scan_from_fixtures(
    *, dup_ticker: str | None = "NVDA", invest_amount: float | None = 100_000,
    core_n: int = 5, top_n: int = 10,
) -> ScanResult:
    """用本地 fixture 组装(0 credit,可复现,供演示与测试)。"""
    holdings = json.load(open(_FIX / "soxx_holdings_2025-12-31.json"))["data"]
    lookup = json.load(open(_FIX / "soxx_lookup.json"))
    tf = json.load(open(_FIX / "soxx_13f_2025Q4.json"))
    prices = json.load(open(_FIX / "soxx_prices_2026-03-23_06-17.json"))
    return build_scan(holdings, lookup, tf, prices,
                      dup_ticker=dup_ticker, invest_amount=invest_amount,
                      core_n=core_n, top_n=top_n)


def build_scan_live(
    etf: str,
    *,
    start_date: str,
    end_date: str,
    year: int | None = None,
    quarter: int | None = None,
    dup_ticker: str | None = "NVDA",
    invest_amount: float | None = 100_000,
    core_n: int = 5,
    top_n: int = 10,
    use_openfigi: bool = True,
    on_progress=None,
) -> ScanResult:
    """接真实 LLMQuant Data 接口组装(消耗 credits:holdings 1 + 13F×top_n)。

    on_progress:可选回调(str)用于打印进度。标的解析仍走人工核对映射表;
    未覆盖的 ETF 会产生 UNRESOLVED(显式标红,不臆测)。
    """
    from ..data import llmquant

    def log(m):
        if on_progress:
            on_progress(m)

    log(f"etf_lookup({etf}) ...")
    lookup = llmquant.etf_lookup(etf)
    log(f"etf_holdings({etf}) ...")
    holdings = llmquant.etf_holdings(etf, limit=500)

    # 标的解析:先用人工映射表;未解析的用 OpenFIGI 自动补(支持任意 ETF)
    extra_map: dict = {}
    res = resolve_holdings(holdings.get("holdings", []))
    if use_openfigi and res.unresolved:
        ids = []
        for h in res.unresolved:
            if h.isin:
                ids.append(("ID_ISIN", h.isin))
            elif h.cusip:
                ids.append(("ID_CUSIP", h.cusip))
        if ids:
            log(f"OpenFIGI 自动解析 {len(ids)} 只未覆盖成分股 ...")
            try:
                from ..resolve.openfigi import resolve_identifiers
                extra_map = resolve_identifiers(ids, on_progress=log)
                res = resolve_holdings(holdings.get("holdings", []), extra_map)
            except Exception as e:  # noqa: BLE001 — 解析失败则退回"标红未解析",不崩
                log(f"OpenFIGI 解析失败(未解析项将标 UNRESOLVED):{e}")

    top_tickers = res.top_n_tickers(top_n)

    tf_raw: dict[str, Any] = {}
    for t in top_tickers:
        log(f"sec_13f_list_ticker_holders({t}) ...")
        tf_raw[t] = llmquant.sec_13f_list_ticker_holders(t, year=year, quarter=quarter)

    log(f"equity_historical_prices({etf}, {start_date}~{end_date}) ...")
    prices = llmquant.equity_historical_prices(etf, start_date=start_date, end_date=end_date)

    return build_scan(holdings, lookup, tf_raw, prices,
                      dup_ticker=dup_ticker, invest_amount=invest_amount,
                      core_n=core_n, top_n=top_n, extra_map=extra_map)
