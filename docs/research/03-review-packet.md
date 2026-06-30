# SOXX Sector Smart Money Scan — 独立复核包 (Review Packet)

> 目的:让外部大模型**不依赖我方代码**即可独立核验全部数字与口径。
> 全部由真实 fixture 程序化生成。数据源:LLMQuant Data(SEC N-PORT / 13F / 价格)。
> 复核重点:① 原始数据是否被如实使用 ② 每个派生数字推导是否正确 ③ 口径是否诚实。

---
## A. 方法论与口径声明
- **数字零 LLM 经手**:所有数值均为对接口返回的确定性计算,LLM 不参与计算。
- 权重为小数转百分比(0.08263→8.263%)。收益用 `adjusted_close`。
- ETF 持仓含现金/货基,**总权重≈102%**;我方将现金单列,不混入股票集中度。
- 13F「持有者数」= SEC Form 13F **Top1000 机构内**持有该票的数量(口径,非全市场)。

## B. 原始输入数据(接口返回,未经修改)
### B1. ETF 概要
- ETF=SOXX | 基金=iShares Semiconductor ETF | AUM=17523822281.57 USD | as_of=2025-12-31 | source=sec_nport | coverage=stale
### B2. 全部 34 行持仓(原始权重 + 解析结果)
| # | holding_name | ISIN | raw weight | →ticker | kind |
|---|---|---|---|---|---|
| 1 | NVIDIA Corp. | US67066G1040 | 0.08263161910302999 | NVDA | equity |
| 2 | Advanced Micro Devices, Inc. | US0079031078 | 0.07720723503016 | AMD | equity |
| 3 | Micron Technology, Inc. | US5951121038 | 0.0696979949628 | MU | equity |
| 4 | Broadcom, Inc. | US11135F1012 | 0.06735639620366 | AVGO | equity |
| 5 | Applied Materials, Inc. | US0382221051 | 0.05883466185766 | AMAT | equity |
| 6 | NXP Semiconductors NV | NL0009538784 | 0.04366060513548 | NXPI | equity |
| 7 | Lam Research Corp. | US5128073062 | 0.04302657428526999 | LRCX | equity |
| 8 | KLA Corp. | US4824801009 | 0.04053252328329 | KLAC | equity |
| 9 | Texas Instruments, Inc. | US8825081040 | 0.04042750044692 | TXN | equity |
| 10 | Analog Devices, Inc. | US0326541051 | 0.04007740274441 | ADI | equity |
| 11 | QUALCOMM, Inc. | US7475251036 | 0.039901604388290005 | QCOM | equity |
| 12 | Taiwan Semiconductor Manufacturing Co. Ltd. | US8740391003 | 0.03844299510777 | TSM | equity |
| 13 | Monolithic Power Systems, Inc. | US6098391054 | 0.03828965029996 | MPWR | equity |
| 14 | Marvell Technology, Inc. | US5738741041 | 0.037272463425220004 | MRVL | equity |
| 15 | ASML Holding NV | USN070592100 | 0.03722013774506 | ASML | equity |
| 16 | Intel Corp. | US4581401001 | 0.03561737027865 | INTC | equity |
| 17 | Microchip Technology, Inc. | US5950171042 | 0.03386179646115 | MCHP | equity |
| 18 | Teradyne, Inc. | US8807701029 | 0.03037657000663 | TER | equity |
| 19 | Astera Labs, Inc. | US04626A1034 | 0.02230710484271 | ALAB | equity |
| 20 | Credo Technology Group Holding Ltd. | KYG254571055 | 0.02210135535883 | CRDO | equity |
| 21 | ON Semiconductor Corp. | US6821891057 | 0.0217726861908 | ON | equity |
| 22 | BlackRock Funds III | US0669225197 | 0.0203109103437 | — | cash |
| 23 | Entegris, Inc. | US29362U1043 | 0.01273019641009 | ENTG | equity |
| 24 | MACOM Technology Solutions Holdings, Inc. | US55405Y1001 | 0.01139813300492 | MTSI | equity |
| 25 | Nova Ltd. | IL0010845571 | 0.010070191595439999 | NVMI | equity |
| 26 | Rambus, Inc. | US7509171069 | 0.009868280651409999 | RMBS | equity |
| 27 | Skyworks Solutions, Inc. | US83088M1027 | 0.009423771779720001 | SWKS | equity |
| 28 | ASE Technology Holding Co. Ltd. | US00215W1009 | 0.00861427274109 | ASX | equity |
| 29 | United Microelectronics Corp. | US9108734057 | 0.00585308433924 | UMC | equity |
| 30 | STMicroelectronics NV | US8610121027 | 0.00546504678153 | STM | equity |
| 31 | ARM Holdings plc | US0420682058 | 0.0047292461809 | ARM | equity |
| 32 | BlackRock Funds III | US0669224778 | 0.00104103310892 | — | cash |
| 33 | BlackRock Funds III | US0669225197 | 1.711e-11 | — | cash |
| 34 | N/A | None | -4.404765e-06 | — | excluded |
### B3. Top10 的 13F(原始返回字段)
| ticker | total_holders_in_scope | aggregate_value_usd | ranking_period | top3 holders |
|---|---|---|---|---|
| NVDA | 779 | 2313965947643 | 2025-12-31 | VANGUARD GROUP INC, STATE STREET CORP, BlackRock, Inc. |
| AMD | 668 | 192549443736 | 2025-12-31 | VANGUARD GROUP INC, STATE STREET CORP, BlackRock, Inc. |
| MU | 644 | 207865468889 | 2025-12-31 | VANGUARD GROUP INC, Capital World Investors, STATE STREET CORP |
| AVGO | 747 | 964592422886 | 2025-12-31 | VANGUARD GROUP INC, STATE STREET CORP, BlackRock, Inc. |
| AMAT | 645 | 123782679478 | 2025-12-31 | VANGUARD GROUP INC, STATE STREET CORP, Capital Research Global Investors |
| NXPI | 469 | 38985291297 | 2025-12-31 | FMR LLC, JPMORGAN CHASE & CO, VANGUARD GROUP INC |
| LRCX | 624 | 132529293939 | 2025-12-31 | VANGUARD GROUP INC, STATE STREET CORP, BlackRock, Inc. |
| KLAC | 584 | 113701628319 | 2025-12-31 | VANGUARD GROUP INC, STATE STREET CORP, Capital International Investors |
| TXN | 642 | 105561026341 | 2025-12-31 | VANGUARD GROUP INC, STATE STREET CORP, BlackRock, Inc. |
| ADI | 590 | 88564160845 | 2025-12-31 | VANGUARD GROUP INC, STATE STREET CORP, BlackRock, Inc. |
### B4. SOXX 价格窗口
- 请求窗口 2026-03-23~2026-06-17 | 实际 2026-03-23~2026-06-17 | 61 交易日
- 起始 close=336.5899963378906 | 结束 close=599.72998046875 | adj 起=336.5899963378906 止=599.72998046875

## C. 派生数字推导(请逐条重算)
- C1 股票仓数=30,现金行=3,剔除/未解析=1,合计应=34
- C2 Top5 = NVDA+AMD+MU+AVGO+AMAT 权重和 = 35.5728%  (公式:前5股票权重相加×100)
- C3 Top10 = 56.3453%  → 其他前十大 = Top10−Top5 = 20.7725%
- C4 其余股票(第11起)= 43.5316% | 现金 = 2.1352% | 剔除 = -0.0004%
- C5 对账:C2+C3其他+C4三项 = 102.0116% 应=总权重 102.0116%
- C6 90天收益 = (end_adj/start_adj −1)×100 = (599.72998046875/336.5899963378906−1)×100 = 78.1782%
- C7 重复暴露:NVDA 权重 8.2632% × $100,000 = $8,263.16

## D. 对账文章(4 重独立校验)
| 校验项 | 我方 | 文章 | 一致? |
|---|---|---|---|
| Top10 集中度 | 56.3% | 56.3% | ✓ |
| Top5(核心)集中度 | 35.6% | 35.6% | ✓ |
| 90天收益 | 78.2% | 78.2% | ✓ |
| 13F holder count(10只) | 见下 | 见下 | ✓ 全等 |

## E. 已知口径差异与我方处理(请评估是否得当)
- **Aggregate 13F Value 比文章低 ~1–7%**:实测与 limit 无关(全量加总)。判断为接口给『申报时点 as-reported 市值』,文章可能按更晚价格重估。差异与个股涨幅正相关(NVDA 最大~7%)。
  **我方处理:保留接口 as-reported 值(有源可复现),不为对齐文章而篡改**,并在数据质量说明中明示口径。请评估此处理是否符合『真实性优先、不臆造』。
- **总权重 102.01%**:因含现金货基。我方将现金单列、占位行纳入对账,未并入股票集中度。

## F. 请复核员重点检查清单
1. B2 表中 30 个 `→ticker` 是否与公司名/ISIN 一一对应正确(尤其 ADR/外资:NXPI/TSM/ASML/CRDO/NVMI/ASX/UMC/STM/ARM)。
2. C2–C7 每个公式与结果是否能用 B 段原始数据手工重算复现。
3. D 段 4 重对账是否成立。
4. E 段口径差异的处理是否专业、是否还有更稳妥做法。
5. 是否存在任何『数字看起来来自模型记忆而非接口』的迹象(应为零)。
