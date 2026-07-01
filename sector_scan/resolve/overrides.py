"""外资 / ADR / 跨市场标的的人工 override 映射(ISIN -> ticker)。

背景:部分外资/ADR 名字,OpenFIGI 按 ISIN 查(即便加 exchCode=US)也**查不到美股主线**,
或只返回带货币后缀的报价线(如 HONGBP/TRI4EUR/AZNN)。这类**不能塞垃圾进 13F**,
需人工核对后 override。优先级与 SOXX 表同级(高于 OpenFIGI)。

⚠️ 每条须经人工/外部复核确认后再加入;查不到又不在此表的,一律标 UNRESOLVED,绝不臆测。
"""
from __future__ import annotations

# ISIN -> (ticker, kind);均为美股主 ticker,已经外部复核确认
OVERRIDE_ISIN_MAP: dict[str, tuple[str | None, str]] = {
    "US4385161066": ("HON", "equity"),   # Honeywell International — NASDAQ:HON(复核确认)
    "CA8849038085": ("TRI", "equity"),   # Thomson Reuters — NASDAQ:TRI(复核确认;非 TRI4EUR)
    "US0463531089": ("AZN", "equity"),   # AstraZeneca ADR — NASDAQ:AZN(复核确认;非 AZNN)
}
