# SOXX 标的映射复核清单 (v1.1 — 已通过 jack + 外部模型复核)

> 由 `sector_scan/resolve/soxx_map.py` + 真实 N-PORT 快照(2025-12-31)程序化生成,非手抄。
> ✅ 复核结论:30 条 ticker 全部正确,无需重映射。
> 口径修正:ASML = NASDAQ NYRS(非 ADR);STM = NYSE NYRS(非 ADR)。

## 一、股票映射(30 条,参与 13F 的 Top10 标 ★)

| # | 名称 | ISIN | CUSIP | 权重 | → Ticker | 核对依据 |
|---|------|------|-------|------|----------|----------|
| 1 ★ | NVIDIA Corp. | US67066G1040 | 67066G104 | 8.263% | **NVDA** | NVIDIA Corp. — NASDAQ:NVDA |
| 2 ★ | Advanced Micro Devices, Inc. | US0079031078 | 007903107 | 7.721% | **AMD** | Advanced Micro Devices — NASDAQ:AMD |
| 3 ★ | Micron Technology, Inc. | US5951121038 | 595112103 | 6.970% | **MU** | Micron Technology — NASDAQ:MU |
| 4 ★ | Broadcom, Inc. | US11135F1012 | 11135F101 | 6.736% | **AVGO** | Broadcom Inc. — NASDAQ:AVGO |
| 5 ★ | Applied Materials, Inc. | US0382221051 | 038222105 | 5.883% | **AMAT** | Applied Materials — NASDAQ:AMAT |
| 6 ★ | NXP Semiconductors NV | NL0009538784 | — | 4.366% | **NXPI** | NXP Semiconductors NV — NASDAQ:NXPI(荷兰注册,美股上市) |
| 7 ★ | Lam Research Corp. | US5128073062 | 512807306 | 4.303% | **LRCX** | Lam Research — NASDAQ:LRCX |
| 8 ★ | KLA Corp. | US4824801009 | 482480100 | 4.053% | **KLAC** | KLA Corp. — NASDAQ:KLAC |
| 9 ★ | Texas Instruments, Inc. | US8825081040 | 882508104 | 4.043% | **TXN** | Texas Instruments — NASDAQ:TXN |
| 10 ★ | Analog Devices, Inc. | US0326541051 | 032654105 | 4.008% | **ADI** | Analog Devices — NASDAQ:ADI |
| 11 | QUALCOMM, Inc. | US7475251036 | 747525103 | 3.990% | **QCOM** | QUALCOMM — NASDAQ:QCOM |
| 12 | Taiwan Semiconductor Manufacturing Co. Ltd. | US8740391003 | 874039100 | 3.844% | **TSM** | Taiwan Semiconductor ADR — NYSE:TSM |
| 13 | Monolithic Power Systems, Inc. | US6098391054 | 609839105 | 3.829% | **MPWR** | Monolithic Power Systems — NASDAQ:MPWR |
| 14 | Marvell Technology, Inc. | US5738741041 | 573874104 | 3.727% | **MRVL** | Marvell Technology — NASDAQ:MRVL |
| 15 | ASML Holding NV | USN070592100 | — | 3.722% | **ASML** | ASML Holding NV — NASDAQ:ASML(NASDAQ registered shares / NYRS,非 ADR) |
| 16 | Intel Corp. | US4581401001 | 458140100 | 3.562% | **INTC** | Intel Corp. — NASDAQ:INTC |
| 17 | Microchip Technology, Inc. | US5950171042 | 595017104 | 3.386% | **MCHP** | Microchip Technology — NASDAQ:MCHP |
| 18 | Teradyne, Inc. | US8807701029 | 880770102 | 3.038% | **TER** | Teradyne — NASDAQ:TER |
| 19 | Astera Labs, Inc. | US04626A1034 | 04626A103 | 2.231% | **ALAB** | Astera Labs — NASDAQ:ALAB |
| 20 | Credo Technology Group Holding Ltd. | KYG254571055 | — | 2.210% | **CRDO** | Credo Technology(开曼注册)— NASDAQ:CRDO |
| 21 | ON Semiconductor Corp. | US6821891057 | 682189105 | 2.177% | **ON** | ON Semiconductor — NASDAQ:ON |
| 22 | Entegris, Inc. | US29362U1043 | 29362U104 | 1.273% | **ENTG** | Entegris — NASDAQ:ENTG |
| 23 | MACOM Technology Solutions Holdings, Inc. | US55405Y1001 | 55405Y100 | 1.140% | **MTSI** | MACOM Technology — NASDAQ:MTSI |
| 24 | Nova Ltd. | IL0010845571 | — | 1.007% | **NVMI** | Nova Ltd(以色列)— NASDAQ:NVMI |
| 25 | Rambus, Inc. | US7509171069 | 750917106 | 0.987% | **RMBS** | Rambus — NASDAQ:RMBS |
| 26 | Skyworks Solutions, Inc. | US83088M1027 | 83088M102 | 0.942% | **SWKS** | Skyworks Solutions — NASDAQ:SWKS |
| 27 | ASE Technology Holding Co. Ltd. | US00215W1009 | 00215W100 | 0.861% | **ASX** | ASE Technology ADR — NYSE:ASX |
| 28 | United Microelectronics Corp. | US9108734057 | 910873405 | 0.585% | **UMC** | United Microelectronics ADR — NYSE:UMC |
| 29 | STMicroelectronics NV | US8610121027 | 861012102 | 0.547% | **STM** | STMicroelectronics NV — NYSE:STM(NYSE registered shares / NYRS,非 ADR) |
| 30 | ARM Holdings plc | US0420682058 | 042068205 | 0.473% | **ARM** | ARM Holdings ADR — NASDAQ:ARM |

## 二、现金 / 货基(3 条,不查 13F)

| 名称 | ISIN | 权重 |
|------|------|------|
| BlackRock Funds III | US0669225197 | 2.031% |
| BlackRock Funds III | US0669224778 | 0.104% |
| BlackRock Funds III | US0669225197 | 0.000% |

## 三、剔除(占位行)

- `N/A`(无标识符,权重 -0.000%)→ EXCLUDED

## 四、汇总

- 股票 30 / 现金 3 / 剔除 1 / 未解析 0
- 股票仓 99.88% | 现金 2.14% | 总计 102.01%
