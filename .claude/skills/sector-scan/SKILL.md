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
