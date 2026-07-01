# 第 7 阶(CLI + Claude Code Skill 打包)复核包

> 目的:审查**打包层**是否保住核心不变量,而非重复数字审计(数字见复核包 v2.1)。
> 关注:① 打包后'数字确定性/零幻觉'是否仍成立 ② SKILL.md 是否规范且契约完整
> ③ CLI 是否正确(含 live==offline 等价证明)④ 有无打包引入的新风险。

## A. 打包必须保住的不变量(请逐条判断是否被破坏)
1. **数字零 LLM 经手**:集中度/收益/重复暴露仍由 Python 确定性计算,agent/CLI 不现算。
2. **标的解析零臆测**:仍走人工核对映射表,未覆盖者标 UNRESOLVED。
3. **解读隔离且受双护栏**:🧠 定性解读无阿拉伯数字、无违禁词,与事实分区。
4. **口径透明**:as_of/source/stale/13F 口径/aggregate 口径仍在输出中。
5. **可降级**:无 DeepSeek Key 或 --no-brain 时,仍出完整事实版。

## B. SKILL.md 全文(实际发布内容)
```markdown
---
name: sector-scan
description: 为行业 ETF 生成一页 Sector Smart Money Scan —— 持仓集中度、13F 机构拥挤度、重复暴露检查、价格窗口收益。当用户想看清 SOXX 等行业 ETF 的真实持仓暴露、机构覆盖广度,或检查"已持有某只个股、再买该 ETF 会否重复暴露"时使用。
input_data_source: LLMQuant Data
category: etfs
---

# Sector Smart Money Scan

把一个行业 ETF 的**真实持仓、13F 机构覆盖度、重复暴露、价格窗口**聚合成一页可复核的中文 dashboard。
所有数字由确定性引擎计算(**不由模型现算**),LLM 只写定性解读。

## 何时使用 (Use When)

- "扫描 SOXX,看前十大持仓 / 机构拥挤度 / 重复暴露 / 90 天表现"
- "我已经持有 NVDA,再买 SOXX 会不会重复暴露?"
- 任意行业 ETF 的持仓集中度 / 机构覆盖度速览

## 如何执行 (How to Run)

本 skill 由确定性 CLI 引擎驱动。解析用户意图后运行:

```bash
python -m sector_scan <ETF> --hold <已持有TICKER> --invest <金额>
# 例:python -m sector_scan SOXX --hold NVDA --invest 100000
```

常用参数:
- `--start YYYY-MM-DD --end YYYY-MM-DD` 价格窗口(默认近 90 天)
- `--year YYYY --quarter 1-4` 指定 13F 季度(默认最新季)
- `--top N`(默认 10) `--core N`(默认 5)
- `--no-brain` 只出确定性事实,不调 DeepSeek 解读
- `--fixtures` 离线用内置 SOXX 快照(0 credit,演示/自测)

把 CLI 的 markdown 输出**原样呈现**给用户;不要改写其中任何数字。

## 数据契约与护栏 (Evidence Contract)

- **数字零模型经手**:集中度、收益、重复暴露全部确定性计算;模型不得自行计算或篡改。
- **标的解析**:持仓 `holding_name/cusip/isin → ticker` 走人工核对映射表;解析不上的显式标红,**绝不臆测**。
- **口径透明**:必须呈现 CLI 输出里的 `as_of` / `source` / `stale` / 13F 口径 / aggregate 口径说明。
- **现金单列**:现金/货基不并入股票集中度(总权重可能 >100%)。
- **解读隔离**:🧠 标注块为 DeepSeek 定性解读(不含阿拉伯数字、不参与计算),与事实表分区。
- **不构成投资建议。**

## 环境 (Setup)

- `LLMQUANT_API_KEY`(必需,数据来源;一次完整扫描约 11 credits)
- `DEEPSEEK_API_KEY`(可选,解读层;缺失或加 `--no-brain` 时自动降级为纯事实版)

## 覆盖范围 (Coverage)

v1 的标的映射表覆盖 **SOXX**(30 只成分股 + 现金识别,已通过外部复核)。
其他 ETF 会对未覆盖成分股标记 UNRESOLVED(不臆测);泛化到任意 ETF 的
OpenFIGI(ISIN/CUSIP→ticker)自动解析为后续升级项。

详细方法论见 [`workflows/sector-smart-money-scan.md`](workflows/sector-smart-money-scan.md)。
```

## C. workflow 方法论全文
```markdown
# Sector Smart Money Scan

## Use When

用户想把一个行业 ETF 的真实持仓、机构覆盖度、重复暴露和价格窗口聚合成一页可复核的 dashboard;
或询问"通过该 ETF 获得行业暴露,实际拿到哪些公司、哪些机构拥挤持仓、多少重复暴露"。

## LLMQuant Data Needed

Required:
- ETF 身份与概要(基金名、AUM、监管快照日期、覆盖状态)—— 用于板块快照。
- ETF 监管持仓(N-PORT)含权重与标识符 —— 用于集中度与成分股解析。
- 逐成分股的 13F 机构持有度(持有者数、合计市值、主要持有人)—— 用于聪明钱矩阵。
- ETF 价格历史(窗口内日线,含 adjusted_close)—— 用于区间收益。

Freshness:
- 报告持仓 `as_of_date`、`source`、`coverage_status`(stale);13F 的 `ranking_period`。
- N-PORT 为监管快照,非实时日度持仓;13F 为季度末延迟披露。

Fallback:
- 缺某项输入时,显式指出缺失的 LLMQuant Data 项,只用已取得的证据继续,不臆造。

## Workflow

1. 确认 ETF、重复暴露标的、投入金额、价格窗口、13F 季度。
2. 拉取 ETF 概要 / 持仓 / 逐成分股 13F / 价格窗口。
3. 解析持仓标的为 ticker(人工核对映射表);现金/货基单列;未解析标红。
4. 确定性计算:集中度分层、区间收益、重复暴露;**数字不经 LLM**。
5. 事实与解读分离:8 模块事实 dashboard + 🧠 定性解读(无数字)。
6. 呈现下方输出格式,并附数据质量说明与风险披露。

## Output Format

1. **一句话速览**(事实 + 🧠 定性解读)
2. **板块快照**:基金名 / AUM / 持仓日期 / 来源 / 覆盖状态 / 集中度 / 收益
3. **持仓集中度**:核心 Top5 / 其他前十 / 其余股票 / 现金(分档对账到总权重)
4. **成分股 × 聪明钱矩阵**:权重 / 13F 持有者数 / 合计市值 / 主要持有人
5. **重复暴露检查**:已持有某股时,投入金额 × 该股权重 = 间接增加暴露
6. **90 天价格窗口**:起止收盘 / 区间收益
7. **数据质量说明**:N-PORT stale、总权重含现金、13F Top1000 口径、aggregate 口径
8. **风险披露**:非投资建议

## Guardrails

- 不编造缺失值;不把模型输出当数据。
- 不把 N-PORT 监管快照当作实时日度持仓。
- 标的映射不确定时标红,不臆测;不混淆同名证券(用 CUSIP/ISIN 兜底)。
- 解读只做定性翻译,不对单只个股收益下判断,不给机构贴数据未提供的分类。
- 不做个性化投资建议。
```

## D. CLI 接口与行为
### D1. --help
```
usage: sector_scan [-h] [--hold HOLD] [--invest INVEST] [--start START]
                   [--end END] [--year YEAR] [--quarter QUARTER] [--top TOP]
                   [--core CORE] [--no-brain] [--fixtures]
                   [etf]

Sector Smart Money Scan

positional arguments:
  etf                行业 ETF 代码(默认 SOXX)

options:
  -h, --help         show this help message and exit
  --hold HOLD        重复暴露检查标的(默认 NVDA;空串关闭)
  --invest INVEST    投入金额,用于重复暴露估算
  --start START      价格窗口起(YYYY-MM-DD,默认近90天)
  --end END          价格窗口止(YYYY-MM-DD,默认今天)
  --year YEAR        13F 年份(默认最新季)
  --quarter QUARTER  13F 季度 1-4(默认最新季)
  --top TOP          Top N 成分股(默认10)
  --core CORE        核心 N 只(默认5)
  --no-brain         不调用 DeepSeek 解读层
  --fixtures         离线:用内置 SOXX 快照(0 credit)
```
### D2. live == offline 等价证明
实时(接真 API,SOXX 文章参数)输出与离线 fixture 输出**逐字一致**(仅尾部换行差异),
证明 live 编排器正确、且与已审计的 fixture 同源。命令:
```
python -m sector_scan SOXX --start 2026-03-23 --end 2026-06-17 --year 2025 --quarter 4 --no-brain
  == python -m sector_scan --fixtures --no-brain   (内容一致)
```
### D3. 错误处理
- 取数失败(网络/无效 ETF)→ CLI 顶层捕获,friendly 报错并返回码 2,不崩栈。
- 解读失败/护栏未过 → 降级为纯事实版,返回码 0。

## E. 本阶两处健壮性修正(反复细查发现,请评估是否得当)
1. **价格排序**:`build_price_window` 原直接取 prices[0]/[-1] 依赖接口升序;
   已改为显式按 `time` 升序排序,防接口顺序变动导致起止价颠倒、收益算反。
2. **quick_reads 键大小写**:解读 JSON 的 ticker 键统一 `.upper()`,防大小写不匹配丢快读。

## F. 请复核员重点检查清单
1. A 段 5 个不变量,打包后是否仍成立?SKILL.md 是否可能诱导 agent **绕过 CLI 自行编数**?
   (SKILL.md 是否足够明确要求'原样呈现 CLI 输出、不改写数字'?)
2. SKILL.md frontmatter 是否符合 Claude Code 规范(name=kebab 且=目录名、description 达意<1536)?
3. workflow 的 Guardrails 是否覆盖:不臆造/不把快照当实时/映射标红/解读不越界?
4. CLI 默认值是否合理(--hold NVDA / --invest 100000 / 近90天窗口 / 最新季 13F)?
   对非 SOXX 的 ETF,行为是否安全(UNRESOLVED 标红而非静默出错)?
5. E 段两处修正是否正确、有无副作用。
6. 是否存在密钥硬编码或泄漏风险(应:仅从环境变量读)。
