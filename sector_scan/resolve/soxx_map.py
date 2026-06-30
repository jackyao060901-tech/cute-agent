"""SOXX 持仓标的映射表(v1,逐个人工核对,零运行时猜测).

为什么需要它:LLMQuant 的 etf_holdings 返回里 `ticker` 全部为 null,只给
holding_name + cusip/isin。要查 13F 必须有 ticker,所以这一步把每个持仓
**确定性地**映射成交易代码。

口径:
- key = ISIN(每个真实持仓都有 ISIN,比 cusip 更全;外资股没有 cusip)。
- value = (ticker, kind)
    kind="equity" -> 正常股票,ticker 为其美股交易代码(ADR 用 ADR 代码)。
    kind="cash"   -> 现金/货币基金(ETF 的现金管理部分),不查 13F。
- 任何不在表内、且非现金、非占位的持仓 -> 解析器标记 UNRESOLVED,**绝不猜**。

⚠️ 这份表是人工编制、供 jack 与其他大模型逐条复核的"事实声明",
   不是接口返回。每条后面注明核对依据。基于 2025-12-31 N-PORT 快照(34 行)。
   下一版升级方向:接 OpenFIGI(ISIN/CUSIP->ticker 权威源)自动泛化到任意 ETF。
"""
from __future__ import annotations

# ISIN -> (ticker, kind)
SOXX_ISIN_MAP: dict[str, tuple[str | None, str]] = {
    "US67066G1040": ("NVDA", "equity"),   # NVIDIA Corp. — NASDAQ:NVDA
    "US0079031078": ("AMD", "equity"),    # Advanced Micro Devices — NASDAQ:AMD
    "US5951121038": ("MU", "equity"),     # Micron Technology — NASDAQ:MU
    "US11135F1012": ("AVGO", "equity"),   # Broadcom Inc. — NASDAQ:AVGO
    "US0382221051": ("AMAT", "equity"),   # Applied Materials — NASDAQ:AMAT
    "NL0009538784": ("NXPI", "equity"),   # NXP Semiconductors NV — NASDAQ:NXPI(荷兰注册,美股上市)
    "US5128073062": ("LRCX", "equity"),   # Lam Research — NASDAQ:LRCX
    "US4824801009": ("KLAC", "equity"),   # KLA Corp. — NASDAQ:KLAC
    "US8825081040": ("TXN", "equity"),    # Texas Instruments — NASDAQ:TXN
    "US0326541051": ("ADI", "equity"),    # Analog Devices — NASDAQ:ADI
    "US7475251036": ("QCOM", "equity"),   # QUALCOMM — NASDAQ:QCOM
    "US8740391003": ("TSM", "equity"),    # Taiwan Semiconductor ADR — NYSE:TSM
    "US6098391054": ("MPWR", "equity"),   # Monolithic Power Systems — NASDAQ:MPWR
    "US5738741041": ("MRVL", "equity"),   # Marvell Technology — NASDAQ:MRVL
    "USN070592100": ("ASML", "equity"),   # ASML Holding NV — NASDAQ:ASML(美股上市线)
    "US4581401001": ("INTC", "equity"),   # Intel Corp. — NASDAQ:INTC
    "US5950171042": ("MCHP", "equity"),   # Microchip Technology — NASDAQ:MCHP
    "US8807701029": ("TER", "equity"),    # Teradyne — NASDAQ:TER
    "US04626A1034": ("ALAB", "equity"),   # Astera Labs — NASDAQ:ALAB
    "KYG254571055": ("CRDO", "equity"),   # Credo Technology(开曼注册)— NASDAQ:CRDO
    "US6821891057": ("ON", "equity"),     # ON Semiconductor — NASDAQ:ON
    "US29362U1043": ("ENTG", "equity"),   # Entegris — NASDAQ:ENTG
    "US55405Y1001": ("MTSI", "equity"),   # MACOM Technology — NASDAQ:MTSI
    "IL0010845571": ("NVMI", "equity"),   # Nova Ltd(以色列)— NASDAQ:NVMI
    "US7509171069": ("RMBS", "equity"),   # Rambus — NASDAQ:RMBS
    "US83088M1027": ("SWKS", "equity"),   # Skyworks Solutions — NASDAQ:SWKS
    "US00215W1009": ("ASX", "equity"),    # ASE Technology ADR — NYSE:ASX
    "US9108734057": ("UMC", "equity"),    # United Microelectronics ADR — NYSE:UMC
    "US8610121027": ("STM", "equity"),    # STMicroelectronics ADR — NYSE:STM
    "US0420682058": ("ARM", "equity"),    # ARM Holdings ADR — NASDAQ:ARM
    # 现金 / 货币基金(BlackRock Funds III = 贝莱德现金管理货基),不查 13F:
    "US0669225197": (None, "cash"),       # BlackRock Funds III(现金扫存)
    "US0669224778": (None, "cash"),       # BlackRock Funds III(另一类别)
}

# 名称兜底:用于 ISIN 缺失但明显是现金/货基的行(防御性,正常用 ISIN 即可命中)。
CASH_NAME_HINTS = ("blackrock funds",)
