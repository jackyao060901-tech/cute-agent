# Sector Smart Money Scan — 准备档案 (Preparation Dossier)

> 状态:准备阶段(未写程序)。本文件汇总落地 `sector-smart-money-scan` skill 之前的全部调研。
> 最后更新:2026-06-30

---

## 0. 任务背景

- **来源**:导师指令 ——「你看看能不能实现一个简单的,从 SOXX 做起」。
- **对标**:LLMQuant Data 旗下 Skills 中的 `sector-smart-money-scan`(公众号 / Substack 文章 demo)。
- **交付仓库**:`cute-agent`,分支 `claude/kai-gong-kai-gong-kai-gong-3n5cvv`。
- **授权**:参考文章只是参考,不要求一模一样;拥有迭代升级权限。
- **本质**:不是让模型即兴写半导体评论,而是通过 `llmquant-data` MCP 调用结构化数据,
  聚合成一页**可复核**的 Sector Smart Money Scan dashboard。

---

## 1. 关键结论(决定怎么做)

1. **官方没有开源 `sector-smart-money-scan` 这个 workflow。**
   `LLMQuant/skills` 仓库 18 个分类里都没有;etfs / equities / investor-lenses 的路由表里也都没有。
   → 我们按官方**格式规范**自建一个,而不是抄文件。这正好对上「迭代升级」的授权。

2. **官方的 skill / workflow 格式规范已逐字拿到**(见第 4 节),可直接套用,保证"地道"。

3. **4 个核心数据工具的真实签名 + 返回字段已确认**(见第 3 节),数据链路完全闭环。

4. **一次完整 SOXX 扫描 ≈ 11 credits**(holdings 1 + 13F×10 + lookup/prices 免费),调试需省着用。

---

## 2. LLMQuant Skills 仓库架构(对标对象)

仓库:`github.com/LLMQuant/skills`(默认分支 **master**)。

```
skills/
  llmquant-<domain>/        # 安装/导入单元 = 一个分类文件夹
    SKILL.md                # 路由器:索引 workflows,强制执行 evidence contract
    workflows/*.md          # 具体可复用流程(输出格式 + guardrails)
    scripts/                # 可选脚本
    assets/                 # 可选资源
templates/
  SKILL_TEMPLATE.md
  WORKFLOW_TEMPLATE.md
.claude-plugin/  .codex-plugin/  .cursor-plugin/   # 各家插件清单
```

**18 个分类**:commodities, credit, crypto, data, equities, equity-derivatives, etfs,
events, investor-lenses, macro, market-intelligence, options, portfolio-lab, portfolio,
prediction-markets, rates-fx, risk, strategies。

**核心设计哲学 —— "Evidence Contract"(数据证据契约)**:
- 用自然语言描述"需要什么数据能力",而非写死工具名 → agent 灵活路由。
- 必须报告 `as_of_date` / source / stale flag / 不支持的 ticker / 缺失字段。
- **Do not estimate holdings from prior knowledge / Do not invent missing values /
  Do not present model output as data.**
- 没接数据源时,workflow 作为可复用模板运行:向用户要数据并标注缺口。

**安装方式**:
- Claude Code 插件市场:`/plugin marketplace add LLMQuant/skills` → `/plugin install llmquant-skills@llmquant`
- CLI:`npx skills add LLMQuant/skills -a codex|cursor|antigravity`

---

## 3. 数据工具真实签名(来自官方 docs.llmquantdata.com)

MCP 包:`@llmquant/data-mcp`,共 ~26 个工具。本 skill 用到 4 个:

### 3.1 `etf_lookup` — 0 credits
- 入参:`ticker`(必填), `as_of?`(YYYY-MM-DD,返回 ≤该日的最近监管快照)
- 返回:`fund_name`, `issuer`, `category`, `expense_ratio`, `aum`, `nav`,
  `holdings_count`, `top_holdings[]`(ticker/holding_name/weight), `sector_exposure[]`,
  `as_of_date`, `stale`, `coverage_status`, `coverage_notice`
- 用途:② Sector Snapshot(基金名 / AUM / 快照日期 / 集中度起点)

### 3.2 `etf_holdings` — 1 credit
- 入参:`ticker`(必填), `limit=50`(max 500), `as_of?`
- 返回:`holdings[]`(`holding_name`, `ticker`, `weight`【小数,0.083=8.3%】,
  `sector`, `country`, `shares`, `market_value`, `cusip`/`isin`…,按 weight 降序),
  `as_of_date`, `coverage_status`
- 用途:③ Concentration(Top10/Top5 集中度)+ 拿到 Top10 成分股清单

### 3.3 `sec_13f_list_ticker_holders` — 1 credit / 票
- 入参:`ticker`(必填), `year?`+`quarter?`(成对,省略=最新季), `limit=100`(max 1000)
- 返回:`ranking_period`, **`total_holders_in_scope`**(= 文章的 "13F Holder Count",
  口径:Top 1000 机构里持有该票的数量), **`aggregate_value_usd`**(= Aggregate 13F Value),
  `holders[]`(`manager_name`, `value_usd`, `shares`…,按 value 降序 → Top Holders)
- 用途:④ Constituent×Smart-Money Matrix + ① One-Line Takeaway

### 3.4 `equity_historical_prices` — 0 credits
- 入参:`ticker`(必填), `start_date`+`end_date`(精确窗口) 或 `limit=30`(近 N 日,max 200)
- 返回:`prices[]`(`open/high/low/close/volume/**adjusted_close**/dividend/stock_split/time`,
  按时间升序)。**算收益用 `adjusted_close`**(已含分红拆股)。
- 用途:⑥ 90-Day Price Window(起始价 / 结束价 / 区间收益)

### 数据链路
```
etf_lookup(SOXX)                       → 基金身份 / AUM / 快照日
etf_holdings(SOXX, limit=10)           → Top10 持仓 + 权重 + 集中度
for tk in Top10:
    sec_13f_list_ticker_holders(tk)    → holder count / aggregate value / top holders
equity_historical_prices(SOXX, 90d)    → 区间收益
```

---

## 4. 官方格式模板(逐字,落地直接套)

### 4.1 SKILL_TEMPLATE(路由器 frontmatter + 结构)
```yaml
---
name: llmquant-category-name
description: Router skill for LLMQuant category workflows. Use when the user needs ...
input_data_source: LLMQuant Data
category: category-name
---
```
结构:Overview → Routing Rules(识别→选择→只打开选中 workflow→用 LLMQuant Data 取数→报告口径)
→ Workflow Index(intent→workflow 表)→ LLMQuant Data Contract(current/future/fallback)
→ Output Requirements(answer + evidence + risk + data provenance)。

### 4.2 WORKFLOW_TEMPLATE(逐字)
```
# Workflow Name

## Use When
Use this workflow when the user asks for ...

## LLMQuant Data Needed
Required:
- Describe the required data capability in natural language, including why it is needed.
Optional or future:
- Describe optional or future data capabilities, including how they would be used.
Freshness:
- State observation dates, filing periods, as-of dates, and stale-data notices.
Fallback:
- If a required input is unavailable, name the missing LLMQuant Data input and continue only with retrieved evidence.

## Workflow
1. Confirm identifiers, horizon, and output target.
2. Pull required LLMQuant Data.
3. Check coverage, dates, and missing fields.
4. Separate evidence from interpretation.
5. Produce the output format below.

## Output Format
1. **Answer**
2. **Evidence**
3. **Scenario / Sensitivity**
4. **Risks / Caveats**
5. **Data Used**

## Guardrails
- Do not invent missing values.
- Do not present model output as data.
- Do not make personalized financial advice claims.
```

### 4.3 真实 workflow 实例参考:`llmquant-etfs/workflows/etf-overlap-report.md`
步骤:Ticker 归一化&lookup → 持仓取数 → 证券匹配(ticker→CUSIP/ISIN 兜底)→ 重叠计算
→ 暴露分析 → 覆盖报告。输出:Bottom Line / ETF Profiles / Overlap Summary / Top Holdings Table
/ Concentration & Exposure Risks / Coverage Caveats / Data Used。
约束:绝不把 N-PORT 当成实时日度持仓;不编造缺失;不混淆同名证券;明确标注覆盖缺口。

---

## 4.4 逐字范本 —— `equity-compare.md`(最接近我们的官方 workflow,含 13F 维度)

```markdown
---
name: Equity Compare
description: Compare 2-5 stocks or ETFs side by side across fundamentals, valuation, technicals, volatility, sentiment, and flow using LLMQuant Data.
input_data_source: LLMQuant Data
pack: research
---

# Equity Compare

## Purpose
Rank a small set of tickers by the dimensions that matter for the user's question ...

## Input Data Source
Use **LLMQuant Data** for all market, fundamental, options, ETF, and ownership evidence. Cite dates and coverage notices for every ticker.

## Data Needed
Required LLMQuant Data inputs:
- equity market snapshot data for price, market cap, sector, liquidity, and recent move.
- company fundamentals data and valuation multiple data ...
- equity technical indicator data and equity price history ...
- implied-volatility snapshot data ...
- ticker-level 13F holder data for institutional sponsorship and crowding.   ← Smart-Money 矩阵官方写法
- ETF identity and profile lookup and ETF holdings data when the compared tickers are ETFs.

## Workflow
1. Accept 2-5 tickers and identify the comparison objective.
2. Pull the same evidence set for each ticker where coverage exists.
3. Normalize units and dates so comparisons are fair.
4. Rank each ticker by dimension and highlight category winners.
5. Produce an overall ranking only after explaining the weights used.

## Output Format
1. **Winner / Ranking**: overall ranking and weighting.
2. **Comparison Table**: price action, quality, valuation, technicals, volatility, flow.
3. **Category Winners**: best quality, cheapest valuation, best momentum, lowest risk.
4. **Decision Notes**: what would change the ranking.
5. **Data Used**: data capabilities, dates, missing fields, stale warnings.

## Guardrails
- Do not compare metrics retrieved on materially different dates without noting it.
- Do not force an overall winner when the user's objective is dimension-specific.
- For ETF comparisons, distinguish holdings overlap from price performance.
```

### 体例要点(从逐字原文提炼)
- workflow `name` 用 **Title Case 人类可读名**("Equity Compare");router SKILL.md `name` 用 **kebab**("llmquant-etfs")。
- workflow frontmatter 用 **`pack:`**(值不固定:etf-overlap=`data`,equity-compare=`research`);router 用 **`category:`**。
- `Data Needed` 一律**自然语言描述能力**,不写死工具名(evidence contract 核心)。
- 每个 workflow 都有 `## Guardrails`,且**最后一节固定是 `Data Used`**(日期/缺失字段/stale)。
- `etf-overlap-report.md` 输出 7 节:Bottom Line / ETF Profiles / Overlap Summary /
  Top Holdings Table / Concentration / Coverage Caveats / Data Used。

## 4.5 Claude Code 官方 Agent Skill 规范(我们最终要合规的标准)

来源:`code.claude.com/docs/en/skills`(遵循 agentskills.io 开放标准)。

- **目录即命令**:`.claude/skills/<dir>/SKILL.md` → `/<dir>`。项目级放 `.claude/skills/`,
  个人级 `~/.claude/skills/`,插件级 `<plugin>/skills/`。
- **frontmatter 字段**:
  | 字段 | 必需 | 说明 |
  |---|---|---|
  | `name` | 必需 | 显示名(插件根 SKILL.md 时它=命令名) |
  | `description` | 推荐 | **驱动自动调用**;关键用途写最前;与 `when_to_use` 合计**截断在 1536 字符** |
  | `when_to_use` | 否 | 触发短语/示例,追加到 description |
  | `argument-hint` | 否 | 自动补全提示,如 `[etf-ticker]` |
  | `disable-model-invocation` | 否 | `true`=只能手动 `/name` 触发 |
  | `allowed-tools` / `disallowed-tools` | 否 | 激活时的工具权限 |
  | `effort` | 否 | low/medium/high/xhigh/max |
- 可**捆绑脚本与参考文件**(skill 目录下),body 按需懒加载——长参考资料几乎零 context 成本。
- 自定义 command 已并入 skill;`/skill-name` 直接调用,或靠 description 自动触发。

### 关键设计取舍(给我们的 skill)
LLMQuant 用的是**插件分发**(`.claude-plugin/marketplace.json` + `skills/llmquant-*/`)。
我们 cute-agent 有两条路:
- **A. 项目级 skill**:`.claude/skills/sector-smart-money-scan/SKILL.md` —— 最简单,克隆即用,
  `/sector-smart-money-scan` 直接触发。**演示首选**。
- **B. 插件包**:`.claude-plugin/marketplace.json` + `skills/...`,对标官方可 `/plugin install`。
  正式分发时再升级到这条。
建议先 A 后 B。frontmatter 同时满足两套规范:`name`+`description`(Claude Code 硬性)
叠加 `input_data_source: LLMQuant Data`(LLMQuant 体例,无害且地道)。

### 官方插件清单(逐字,打包时照抄结构)
```json
// .claude-plugin/marketplace.json
{
  "name": "llmquant",
  "owner": { "name": "LLMQuant", "url": "https://llmquant.com" },
  "description": "Finance research, trading, risk, and portfolio Agent Skills grounded in LLMQuant Data.",
  "version": "0.1.0",
  "plugins": [
    { "name": "llmquant-skills", "source": ".", "description": "...", "version": "0.1.0",
      "homepage": "https://github.com/LLMQuant/skills", "license": "MIT" }
  ]
}
```

---

## 5. 环境变量(接 MCP 时)

| 变量 | 用途 | 默认 |
|---|---|---|
| `LLMQUANT_API_KEY` | 认证(stdio 必填) | (待获取) |
| `LLMQUANT_BASE_URL` | API 地址 | `https://api.llmquantdata.com` |
| `LLMQUANT_API_TIMEOUT_MS` | 超时 | `15000` |
| `LLMQUANT_MCP_TRANSPORT` | 传输 | `stdio` |

接入命令(Claude Code):
```
claude mcp add llmquant-data -e LLMQUANT_API_KEY=<key> -- npx -y @llmquant/data-mcp
```
工具在 Claude Code 内调用名预计为 `mcp__llmquant-data__<tool>`(待 Key 到后实测确认)。

---

## 6. 目标产物设计(草案 — 待拍板)

把 SOXX skill 做成一个**遵循官方规范**的分类 skill,放在 cute-agent 仓库:
```
skills/
  sector-smart-money/         # 或并入 llmquant 风格命名
    SKILL.md                  # 路由器
    workflows/
      sector-smart-money-scan.md
    assets/
      soxx-sample.json        # 文章样例数据,用作无 Key 时的 mock / 自测基准
```
8 个输出模块(对标文章,可升级):One-Line Takeaway / Sector Snapshot / Holdings Concentration
/ Constituent×Smart-Money Matrix / Duplicate Exposure Check / 90-Day Price Window
/ Data Quality Notes / Risk Disclosure。

### 可升级点(用好"迭代"授权)
- **Duplicate Exposure 做成真计算**:持有金额 × ETF 内 NVDA 权重 = 间接增加的 NVDA 暴露(文章只定性提)。
- **集中度自动分层**:Top5 / Top10 / 其余,直接从 holdings 算,不写死。
- **口径严谨**:13F holder count 注明是"Top 1000 机构内"口径(文章未点破)。
- **泛化**:参数化 `sector_etf`,不只 SOXX —— 一套跑 SMH/XLK/IGV 等任意行业 ETF。
- **可选可视化**:集中度饼图 / holder bar(文章用字符条,可升级成图)。
- **双语输出**:英文模块名 + 中文解读(对标文章风格)。

---

## 7. 待拍板的设计决策

1. 输出语言:中文 / 英文 / 双语?
2. 用途定位:券商/导师演示 vs 真用工具(影响容错严谨度)。
3. Key 到之前是否先做 mock 演示版。
4. skill 命名与目录结构(是否完全照搬 `llmquant-*` 风格)。

---

## 8. 资料来源

- 公众号原文(参考)/ Substack 英文版:When You Buy SOXX, What Are You Actually Holding?
- `github.com/LLMQuant/skills`(skill 格式规范、模板、etf-overlap 实例)
- `github.com/LLMQuant/data-mcp`(MCP 工具、.env.example)
- `docs.llmquantdata.com`(各工具参数页、llms.txt 索引)
