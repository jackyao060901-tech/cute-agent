"""OpenFIGI 标的解析(免费):ISIN/CUSIP -> 美股 ticker + 证券类型分类。

用于把 SOXX 人工映射表未覆盖的成分股自动解析,支持任意 ETF。
- 优先取 exchCode="US"(美国综合)的条目;
- 证券类型含 fund/money market -> 归为现金(不查 13F);其余 Equity -> 股票;
- 结果落地缓存(避免重复调用 + 限流);OpenFIGI 返回真实映射,非模型臆测。

无 API key:25 请求/分钟、每请求 ≤10 个;本模块自动分批 + 节流。
可设环境变量 OPENFIGI_API_KEY 提高配额。
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

FIGI_URL = "https://api.openfigi.com/v3/mapping"
_CACHE = Path(__file__).resolve().parent.parent / "data" / "figi_cache.json"
_FUND_HINTS = ("fund", "money market", "unit investment trust")


class OpenFigiError(RuntimeError):
    pass


def _classify(item: dict) -> str | None:
    st = f"{item.get('securityType') or ''} {item.get('securityType2') or ''}".lower()
    if any(h in st for h in _FUND_HINTS):
        return "cash"
    if item.get("marketSector") == "Equity" or item.get("ticker"):
        return "equity"
    return None


def _pick(data: list[dict]) -> dict | None:
    us = [d for d in data if d.get("exchCode") == "US" and d.get("ticker")]
    for pool in (us, [d for d in data if d.get("ticker")]):
        if pool:
            return pool[0]
    return None


def _load_cache() -> dict:
    if _CACHE.exists():
        try:
            return json.load(open(_CACHE, encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_cache(cache: dict) -> None:
    _CACHE.parent.mkdir(parents=True, exist_ok=True)
    json.dump(cache, open(_CACHE, "w", encoding="utf-8"), ensure_ascii=False, indent=0)


def _post(jobs: list[dict], api_key: str | None) -> list[dict]:
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["X-OPENFIGI-APIKEY"] = api_key
    req = urllib.request.Request(
        FIGI_URL, data=json.dumps(jobs).encode("utf-8"), headers=headers, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise OpenFigiError(f"HTTP {e.code}: {e.read().decode('utf-8','replace')[:200]}") from e
    except urllib.error.URLError as e:
        raise OpenFigiError(f"网络失败:{e}") from e


def resolve_identifiers(
    ids: list[tuple[str, str]], api_key: str | None = None, on_progress=None
) -> dict[str, tuple[str | None, str] | None]:
    """ids: [(idType, idValue), ...],idType ∈ ID_ISIN/ID_CUSIP。

    返回 {idValue: (ticker, kind)} 或 {idValue: None}(无匹配)。带持久缓存。
    """
    api_key = api_key or os.environ.get("OPENFIGI_API_KEY")
    cache = _load_cache()
    out: dict[str, tuple[str | None, str] | None] = {}
    todo = []
    for idtype, idval in ids:
        ck = f"{idtype}:{idval}"
        if ck in cache:
            v = cache[ck]
            out[idval] = tuple(v) if v else None
        else:
            todo.append((idtype, idval))

    batch = 100 if api_key else 10
    delay = 0.3 if api_key else 2.6  # 无 key 时 ~25/min
    for i in range(0, len(todo), batch):
        chunk = todo[i:i + batch]
        if on_progress:
            on_progress(f"OpenFIGI 解析 {i + 1}-{i + len(chunk)}/{len(todo)} ...")
        results = _post([{"idType": t, "idValue": v} for t, v in chunk], api_key)
        for (idtype, idval), r in zip(chunk, results):
            data = r.get("data") or []
            item = _pick(data)
            val = None
            if item:
                kind = _classify(item)
                if kind:
                    val = (item.get("ticker") if kind == "equity" else None, kind)
            cache[f"{idtype}:{idval}"] = list(val) if val else None
            out[idval] = val
        if i + batch < len(todo):
            time.sleep(delay)
    _save_cache(cache)
    return out
