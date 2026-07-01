# cute-agent · Sector Smart Money Scan

用 agent 做出满足量化投资需求的 skill —— 第一个是 **Sector Smart Money Scan**:
把一个行业 ETF 的**真实持仓、13F 机构拥挤度、重复暴露、价格窗口**聚合成一页可复核的中文 dashboard(从 SOXX 做起)。

> 核心原则:**数字零 LLM 经手**(全部确定性计算),LLM 只写定性解读;每个数据挂来源与日期,拿不到就标缺失,绝不臆造。详见 [`CLAUDE.md`](CLAUDE.md)。

## 快速上手

```bash
# 环境变量(不硬编码进源码)
export LLMQUANT_API_KEY=...     # 数据(持仓/13F/价格),一次扫描约 11 credits
export DEEPSEEK_API_KEY=...     # 解读(可选;缺失时自动降级为纯事实版)

# 离线演示(用内置 SOXX 快照,0 credit)
python -m sector_scan --fixtures --no-brain

# 实时扫描
python -m sector_scan SOXX --hold NVDA --invest 100000
python -m sector_scan SOXX --start 2026-03-23 --end 2026-06-17 --year 2025 --quarter 4
```

也可作为 **Claude Code skill** 使用:`/sector-scan SOXX`(见 [`.claude/skills/sector-scan/`](.claude/skills/sector-scan/))。

## 架构(分层,便于迭代)

```
sector_scan/
  config.py            # 密钥/配置(只从环境读)
  data/llmquant.py     # LLMQuant Data 接口封装(etf_lookup/holdings/13F/prices)
  resolve/             # 标的解析:holding_name/isin -> ticker(人工核对映射表,零臆测)
  scan/compute.py      # 集中度分层 + 重复暴露(确定性)
  scan/scan.py         # 编排器(fixture / live 两入口)
  scan/render.py       # 8 模块中文 dashboard(只放事实)
  brain/               # DeepSeek 解读层(定性,数字+违禁词双护栏)
  cli.py               # 命令行入口
  fixtures/            # 真实快照,作 golden fixture(测试零额度)
tests/                 # 7 组测试,均用 fixture,不花 credits
docs/                  # 调研档案、复核包、样张
```

## 输出的 8 个模块

一句话速览 · 板块快照 · 持仓集中度 · 成分股×聪明钱矩阵 · 重复暴露检查 · 90天价格窗口 · 数据质量说明 · 风险披露

## 质量保证

- 对标文章**四重独立对账**:Top10 ticker / 13F holder count / 集中度 / 90天收益 全部吻合。
- 标的映射与大脑解读经**外部大模型多轮复核**(见 `docs/research/`)。
- 测试全部用 golden fixture,零额度、可复现。

> 本项目仅供信息研究,不构成投资建议。ETF 持仓来自 SEC N-PORT 监管快照;13F 为延迟披露的季度末仓位。
