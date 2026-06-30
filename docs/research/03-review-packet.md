# SOXX Sector Smart Money Scan — 独立复核包 (Review Packet) v2.1

> 目的:让外部大模型**不依赖我方代码**即可独立核验全部数字与口径。
> 数据源:LLMQuant Data(SEC N-PORT / 13F / 价格),由真实 fixture 程序化生成。
> v2.1 变更:据二轮复核,封死 3 处展示精度的误解空间(C5/B4/E1),数学未变。

---
## A. 方法论与口径声明
- **数字零 LLM 经手**:所有数值均为对接口返回的确定性计算,LLM 不参与计算。
- 权重为小数转百分比(0.08263→8.263%)。收益用 `adjusted_close`。
- ETF 持仓含现金/货基,**总权重≈102%**;我方将现金单列,不混入股票集中度。
- 13F「持有者数」= SEC Form 13F **Top1000 机构内**持有该票的数量(口径,非全市场)。
- 证券类型口径:ASML=NASDAQ registered shares/NYRS,STM=NYSE NYRS,均**非普通 ADR**。
- **展示精度约定**:正文百分比/金额为展示用四舍五入;一切派生量以 B 段未四舍五入原始值计算。

## B. 原始输入数据(接口返回,未经修改)
### B1. ETF 概要
- ETF=SOXX | 基金=iShares Semiconductor ETF | AUM=17523822281.57 USD | as_of=2025-12-31 | source=sec_nport | coverage=stale
### B2. 全部 34 行持仓(原始权重 + 解析结果)
> 注:本表按**接口原始顺序**排列(含穿插的现金行 22/32/33),非按权重重排。
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
- 请求窗口 2026-03-23~2026-06-17(文章称『90 天』;**实为约 3 个月 / 86 天间隔(含首尾 87 个自然日期)/ 61 交易日**)
- 起始 close=336.5899963378906 | 结束 close=599.72998046875 | adj 起=336.5899963378906 止=599.72998046875

## C. 派生数字推导(请逐条重算)
- C1 股票仓数=30,现金行=3,剔除/未解析=1,合计应=34
- C2 Top5(核心)= NVDA+AMD+MU+AVGO+AMAT 权重和 = **35.5728%**
- C3 Top10 = **56.3453%** → 其他前十大 = Top10−Top5 = **20.7725%**
- C4 其余股票 = **第 11 名起的 equity 行(不含 cash / excluded)** = **43.5316%**
- C4b 现金 = 2.1352% | 剔除/未解析 = -0.0004%
- **C5 完整对账(显式列全 5 项;用 B2 未四舍五入原始权重计算)**:
  ```
  Top5 + 其他前十大 + 其余equity + cash + excluded
  = 102.0116009%   ≈ 102.0116%   (= 总权重)
  ```
  注:若直接把上方各档**展示值(4位)**相加得 102.0117%,与精确值 102.0116009% 的微差
  纯属展示精度,非计算误差。『仅股票部分』= Top5+其他前十+其余equity = 99.8768%(**不是总权重**)。
- C6 收益 = (end_adj/start_adj −1)×100 = (599.72998046875/336.5899963378906−1)×100 = **78.1782%**
- C7 重复暴露:NVDA 权重 8.2632% × \$100,000 = **\$8,263.1619**

## D. 对账文章(逐项,自洽)
### D1. 集中度 / 收益
| 校验项 | 我方 | 文章 | 一致? |
|---|---|---|---|
| Top10 集中度 | 56.3% | 56.3% | ✓ |
| Top5(核心)集中度 | 35.6% | 35.6% | ✓ |
| 价格窗口收益 | 78.2% | 78.2% | ✓ |
### D2. 13F Holder Count(按 ETF 权重序)
| ticker | 我方 | 文章 | 一致? |
|---|---|---|---|
| NVDA | 779 | 779 | ✓ |
| AMD | 668 | 668 | ✓ |
| MU | 644 | 644 | ✓ |
| AVGO | 747 | 747 | ✓ |
| AMAT | 645 | 645 | ✓ |
| NXPI | 469 | 469 | ✓ |
| LRCX | 624 | 624 | ✓ |
| KLAC | 584 | 584 | ✓ |
| TXN | 642 | 642 | ✓ |
| ADI | 590 | 590 | ✓ |

→ 10 只 holder count 全部一致 ✓。

## E. 已知口径差异与我方处理(请评估是否得当)
### E1. Aggregate 13F Value:我方与文章公布值的差异(逐只)
> 注1:此处『差异』是**与文章公布值之差**;并不预设文章为基准真值——两者估值基准可能不同。
> 注2:百分比差异用 **B3 的精确 `aggregate_value_usd`** 与文章公布值计算;下表 $T/$B 金额为展示用四舍五入,直接拿展示值反算会有微差。
| ticker | 我方(展示) | 文章 | 我方相对文章(精确算) |
|---|---|---|---|
| NVDA | $2.31T | $2.48T | -6.69% |
| AMD | $192.55B | $196.30B | -1.91% |
| MU | $207.87B | $211.33B | -1.64% |
| AVGO | $964.59B | $980.41B | -1.61% |
| AMAT | $123.78B | $126.69B | -2.29% |
| NXPI | $38.99B | $39.91B | -2.32% |
| LRCX | $132.53B | $137.72B | -3.77% |
| KLAC | $113.70B | $114.98B | -1.11% |
| TXN | $105.56B | $106.55B | -0.93% |
| ADI | $88.56B | $89.69B | -1.26% |

→ 我方系统性低于文章 **约 0.9%–6.7%**(最小 TXN,最大 NVDA)。
### E2. 我方处理与假设标注
- **处理(原则)**:保留接口 as-reported 全量值(有源、可复现),**不为对齐文章而改写**。
- **证据(limit 敏感性)**:实测 NVDA `limit=100` 与 `limit=1000` 的 aggregate 均为 \$2.314T(返回行数 100→779,合计不变)→ 据此推断为**全量加总**;未对全部 ticker 做 limit 敏感性测试。
- **假设(非事实)**:文章更高值**可能**源于不同估值基准(如更晚的市价重估)。此为 *hypothesis*,我方未掌握文章计算细节,故不作结论。
- 总权重 102.01%:因含现金货基;现金单列、占位行纳入对账,未并入股票集中度。

## F. 请复核员重点检查清单
1. B2 表 30 个 `→ticker` 是否与公司名/ISIN 一一对应(尤其 ADR/外资/NYRS:NXPI/TSM/ASML/CRDO/NVMI/ASX/UMC/STM/ARM)。
2. C2–C7 是否能用 B 段原始数据手工重算复现;C5 以未四舍五入权重核对 = 总权重。
3. D1/D2 对账是否成立。
4. E1 差异(用精确值算)与 E2 的『处理/证据/假设』三分是否专业。
5. 是否存在任何『数字看起来来自模型记忆而非接口』的迹象(应为零)。
