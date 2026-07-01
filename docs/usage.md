# 使用指南 (How to Use) —— Sector Smart Money Scan

从零到跑通,照着做即可。分两种人:**想在自己电脑上用** / **在 Claude Code 里用**。

---

## A. 在自己电脑上用(命令行)

### 第 0 步 · 装好前提
- **Python 3.10+**(命令行敲 `python3 --version` 能看到版本就行)
- 不需要装任何第三方库(本工具只用 Python 标准库)

### 第 1 步 · 拿到代码
```bash
git clone <这个仓库地址> cute-agent
cd cute-agent
```

### 第 2 步 · 先跑离线演示(不用钥匙、不花钱)
先确认能跑起来。这一步用内置的 SOXX 快照,**零花费**:
```bash
python3 -m sector_scan --fixtures --no-brain
```
👉 屏幕上应打印出一页 SOXX 报告(8 个模块)。看到就说明装好了。

### 第 3 步 · 配两把钥匙(要用真实数据/AI 解读才需要)
```bash
export LLMQUANT_API_KEY=lqd_data_你的key      # 数据(持仓/13F/价格)
export DEEPSEEK_API_KEY=sk_你的key            # AI 解读(可选)
```
> Windows PowerShell 用:`$env:LLMQUANT_API_KEY="..."`

### 第 4 步 · 跑真实扫描
```bash
python3 -m sector_scan SOXX
```
它会逐步调接口(屏幕左侧出现 `· etf_lookup...` 之类进度),最后打印带 🧠 解读的完整报告。
一次完整 SOXX 扫描约 **11 credits**。

### 第 5 步 · 常用玩法
```bash
# 检查"已持有 NVDA、再买 SOXX"的重复暴露
python3 -m sector_scan SOXX --hold NVDA --invest 100000

# 只要事实、不要 AI(更快、不用 DeepSeek key)
python3 -m sector_scan SOXX --no-brain

# 导出交付版
python3 -m sector_scan SOXX --html --out soxx.html      # 网页
python3 -m sector_scan SOXX --pdf soxx.pdf              # PDF(需本机 Chromium)

# 复现文章口径(指定价格窗口 + 13F 季度)
python3 -m sector_scan SOXX --start 2026-03-23 --end 2026-06-17 --year 2025 --quarter 4
```

---

## B. 在 Claude Code 里用(技能)

本仓库已内置技能 `.claude/skills/sector-scan/`。在 Claude Code 里直接用大白话说,例如:
> **用 sector-scan 扫描 SOXX,我已持有 NVDA、投入 10 万,看重复暴露和 90 天表现**

Claude 会自动去跑对应命令并把报告呈现给你。前提是运行环境里已设好 `LLMQUANT_API_KEY`。

---

## 参数速查

| 参数 | 作用 | 默认 |
|---|---|---|
| `etf`(位置参数) | 目标行业 ETF | SOXX |
| `--hold X` | 重复暴露检查标的 | 仅 SOXX 缺省 NVDA,其他关闭 |
| `--no-hold` | 显式关闭重复暴露检查 | — |
| `--invest 金额` | 投入金额(算间接暴露) | 100000 |
| `--start / --end` | 价格窗口(YYYY-MM-DD) | 近 90 天 |
| `--year / --quarter` | 13F 季度 | 最新季 |
| `--top / --core` | 前 N 大 / 核心 N 只 | 10 / 5 |
| `--no-brain` | 不调 DeepSeek,只出事实 | — |
| `--fixtures` | 离线用内置 SOXX 快照(0 credit) | — |
| `--html` / `--pdf 文件` / `--out 文件` | 导出格式 | markdown 到屏幕 |

---

## 常见问题 (Troubleshooting)

- **`缺少 LLMQUANT_API_KEY`**:没设钥匙。先 `export LLMQUANT_API_KEY=...`,或加 `--fixtures --no-brain` 走离线。
- **`Ticker XXX is not currently supported`**:ETF 代码打错或不支持,换一个;程序会友好报错、退出码 2,不会崩。
- **报告顶部出现"⚠️ 覆盖提示 ... 集中度/矩阵不适用"**:该 ETF 的成分股当前映射表未覆盖(v1 只精确支持 **SOXX**)。ETF 概要与价格仍有效;泛化到任意 ETF 是后续升级(接 OpenFIGI/SEC EDGAR)。
- **`--fixtures` 报错说只支持 SOXX**:离线快照只有 SOXX;其他 ETF 请去掉 `--fixtures` 走实时。
- **PDF 导出失败**:本机没 Chromium。设 `CHROME_BIN=/path/to/chrome`,或先 `--html` 导出后用浏览器"打印为 PDF"。

> 本工具仅供信息研究,不构成投资建议。详见 `docs/disclaimer.md`、`docs/methodology.md`。
