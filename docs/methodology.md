# Sector Smart Money Scan — 方法论 (Methodology)

> 版本:v1(SOXX)。本文件说明每个数字的来源、口径与计算方式,供券商/机构复核。
> 最高原则:**数字零 LLM 经手** —— 全部确定性计算;LLM 只写定性解读,且受双护栏约束。

---

## 1. 数据来源 (Data Sources)

全部来自 **LLMQuant Data**(`@llmquant/data-mcp` / REST `api.llmquantdata.com`),四个接口:

| 用途 | 接口 | 关键字段 | 时效口径 |
|---|---|---|---|
| ETF 概要 | `etf_lookup` | fund_name, aum, holdings_count | 监管快照,`as_of_date` |
| ETF 持仓 | `etf_holdings` | holding_name, isin/cusip, weight | SEC **N-PORT** 监管快照(非实时) |
| 机构持有 | `sec_13f_list_ticker_holders` | total_holders_in_scope, aggregate_value_usd, holders[] | SEC **Form 13F**,季度末、延迟披露 |
| 价格 | **免费源**:Yahoo(主,复权价)+ Nasdaq(备)| adjusted_close/close/time | 回退+交叉校验,见 §6 |

**时效声明**:N-PORT 与 13F 均为**监管披露、有滞后**,不等于实时日度持仓;报告始终呈现 `as_of_date` / `ranking_period` / `coverage_status`。

## 2. 处理流水线 (Pipeline)

```
etf_lookup + etf_holdings → 标的解析 → 确定性计算 → 8模块事实渲染 → (可选)DeepSeek 定性解读
                                              ↑ 逐成分股 13F + 价格窗口
```
分层:`data`(取数)→ `resolve`(解析)→ `scan/compute`(计算)→ `scan/render`(渲染)→ `brain`(解读)。

## 3. 标的解析 (Ticker Resolution)

- N-PORT 返回的 `ticker` 恒为 null,仅有 `holding_name` + `cusip`/`isin`;而 13F 查询需 ticker。
- 采用**人工核对的映射表**(`resolve/soxx_map.py`,键=ISIN),每条附核对依据,**已通过外部大模型多轮复核**。
- **现金/货基**(如 BlackRock Funds III)识别为 `cash`,**单列、不并入股票集中度**。
- **占位行**(N/A、无标识符)剔除。
- **未解析**成分股标记 `UNRESOLVED`,在数据质量说明显式披露数量与名称,**绝不臆测、不静默丢弃**。
- **解析两级(支持任意 ETF)**:① SOXX 用上述人工核对表(最可信);② 其余成分股用 **OpenFIGI**
  (免费权威源)自动 ISIN/CUSIP→ticker,并按证券类型把货基/基金归为现金。OpenFIGI 返回真实映射、
  非模型臆测;结果本地缓存以省调用。人工表优先级高于 OpenFIGI。

## 4. 集中度 (Concentration)

- 权重用 N-PORT **原始值**(小数),总和 ≈102%(因含现金),**如实保留**。
- 分档(可对账到总权重):
  - **核心 Top5**:权重最高 5 只股票之和
  - **其他前十大**:Top10 − Top5
  - **其余股票**:第 11 名起的股票
  - **现金及等价物**:单列
  - **占位/未解析**:纳入对账(通常≈0)
- 对账:五档相加 = 总权重(以未四舍五入原始值计)。

## 5. 机构指标 (13F Metrics)

- **持有者数** = `total_holders_in_scope`:SEC Form 13F **Top 1000 机构内**持有该票的数量(**非全市场**)。
- **合计 13F 市值** = `aggregate_value_usd`:全量加总(实测与 `limit` 无关),为**申报时点 as-reported 市值**;与第三方按更晚价格重估的数字可能有数个百分点差异——**保留接口值,不为对齐而改写**。
- **主要持有人**:`holders[]` 按 `value_usd` 降序取前若干;仅表示"按持仓市值最大的机构",**不代表其重仓/主导,亦不含主动/被动分类**。

## 6. 收益 (Return)

- 区间收益 = `(end_adjusted_close / start_adjusted_close − 1) × 100`。
- 用 `adjusted_close`(含分红/拆股);价格按 `time` 升序取窗口首末交易日。
- **价格源(免费)**:Yahoo 主(有复权价)+ Nasdaq 备。**回退**:主源失败自动切备源。
  **交叉校验**:两源都返回时比末日收盘,吻合/背离如实记入数据质量说明;记录本次所用来源(可复现)。
  注:不同源复权口径可能有零点几个百分点差异,均为各自"as-adjusted",非错误。
- 报告明示实际窗口与交易日数;"90 天"为名义窗口(约 3 个月),非精确 90 自然日。

## 7. 重复暴露 (Duplicate Exposure)

- 若已持有标的 `T` 且 `T` 在 ETF 中权重为 `w`,则每投入金额 `A`,间接增加 `T` 暴露 = `A × w`。
- 例:NVDA 权重 8.26%,投入 $100,000 → 间接 +$8,263。

## 8. 防幻觉护栏 (Anti-Hallucination)

- **数字**:全部由上述确定性公式计算,LLM 不参与;测试用 golden fixture 逐项复算。
- **解读**(DeepSeek):
  - **禁止任何阿拉伯数字**(数字只在事实表);
  - **违禁词护栏**:主导/重仓/控制/被动/收益强劲等越界词一律拦截、重试;
  - 不对单只个股收益下判断;不给机构贴数据未提供的分类;
  - 违规重试,仍违规则**降级**(仅出事实版),解读永不阻塞事实。
  - 解读全部置于 🧠 标注块,与事实视觉分区。

## 9. 已知局限 (Limitations)

- **支持任意美股 ETF**(SOXX 人工表 + OpenFIGI 自动解析);极少数纯衍生品成分股会标 UNRESOLVED。
- 数据源仍为付费 LLMQuant(持仓/13F/价格);"换免费源(SEC EDGAR / 基金公司每日持仓)"为后续升级。
- N-PORT / 13F 为监管快照,有披露滞后;不构成实时持仓。
- Aggregate 13F 市值为申报时点口径,跨源比较需注意估值基准差异。

## 10. 复现与审计 (Reproducibility)

- 每个数据接口的原始返回存为 `fixtures/*.json`(golden fixture),测试零额度、可复现。
- 独立复核包见 `docs/research/03-review-packet.md`(数字)、`04/05`(打包)。
- 对文章四重独立对账全部吻合(见 `docs/benchmark.md`)。

> **本文件所述为信息研究方法论,不构成投资建议。** 见 `docs/disclaimer.md`。
