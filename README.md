# Sector Smart Money Scan · 使用说明书

一条命令,生成一页某行业 ETF 的 **Sector Smart Money Scan**:真实持仓集中度、13F 机构拥挤度、
重复暴露检查、价格窗口收益(从 SOXX 做起)。

> **核心原则**:所有**数字**由确定性计算得出、**零 LLM 经手**;AI 只写文字解读且受护栏约束。
> 每个数据都挂来源与日期,拿不到就标缺失,绝不臆造。详见 [`docs/methodology.md`](docs/methodology.md)。

---

## 目录
1. [安装](#1-安装) · 2. [配置钥匙](#2-配置钥匙) · 3. [快速开始](#3-快速开始) ·
4. [完整命令](#4-完整命令) · 5. [参数表](#5-参数表) · 6. [导出](#6-导出报告) ·
7. [示例集](#7-示例集) · 8. [常见问题](#8-常见问题) · 9. [说明](#9-重要说明)

---

## 1. 安装

需要 **Python 3.10+**(敲 `python3 --version` 能看到版本即可),**无需安装任何第三方库**。

把收到的代码文件夹放到本地,进入该目录:
```bash
# 如果收到的是压缩包,先解压;然后进入代码目录(目录里应能看到 sector_scan/ 文件夹)
cd 代码所在目录
```

先验证能跑(离线、不花钱、不用钥匙):
```bash
python3 -m sector_scan --fixtures --no-brain
```
看到一页 SOXX 报告 = 装好了。

---

## 2. 配置钥匙

两把钥匙、两个角色:**LLMQuant = 数据(数字)**;**DeepSeek = 大脑(文字解读)**。

```bash
# Linux / macOS / WSL
export LLMQUANT_API_KEY='你的_lqd_data_key'     # 数据:持仓/13F/价格(付费,一次扫描约 11 credits)
export DEEPSEEK_API_KEY='你的_sk_key'            # 解读:可选,缺失或加 --no-brain 时自动降级为纯事实版
```
```powershell
# Windows PowerShell
$env:LLMQUANT_API_KEY="你的_lqd_data_key"
$env:DEEPSEEK_API_KEY="你的_sk_key"
```

---

## 3. 快速开始

```bash
# 最常用:真实扫描 SOXX + AI 解读
python3 -m sector_scan SOXX

# 检查"已持有 NVDA、再买 SOXX"的重复暴露
python3 -m sector_scan SOXX --hold NVDA --invest 100000
```
运行时屏幕左侧会打印接口调用进度(`· etf_lookup...`),最后输出 8 模块报告。

---

## 4. 完整命令

**基本结构**:
```bash
python3 -m sector_scan [ETF代码] [参数...]
```

**所有用法**:
```bash
# 1) 真实扫描(默认:最新数据 + AI 解读)
python3 -m sector_scan SOXX

# 2) 重复暴露检查(已持有某股,投入某金额)
python3 -m sector_scan SOXX --hold NVDA --invest 100000
python3 -m sector_scan SOXX --hold AMD  --invest 50000
python3 -m sector_scan SOXX --no-hold                       # 不做重复暴露检查

# 3) 只要事实、不要 AI 解读(更快,不用 DeepSeek)
python3 -m sector_scan SOXX --no-brain

# 4) 指定价格窗口 / 13F 季度(不填=自动用最新)
python3 -m sector_scan SOXX --start 2026-03-23 --end 2026-06-17
python3 -m sector_scan SOXX --year 2025 --quarter 4
python3 -m sector_scan SOXX --start 2026-03-23 --end 2026-06-17 --year 2025 --quarter 4   # 复现文章 +78.2%

# 5) 调整集中度分档(核心 N 只 / 前 N 大)
python3 -m sector_scan SOXX --core 3 --top 6

# 6) 导出网页 / PDF
python3 -m sector_scan SOXX --html --out soxx.html
python3 -m sector_scan SOXX --pdf soxx.pdf

# 7) 离线演示(0 花费,用内置 SOXX 快照,不用钥匙)
python3 -m sector_scan --fixtures
python3 -m sector_scan --fixtures --no-brain
python3 -m sector_scan --fixtures --html --out demo.html

# 8) 查看帮助
python3 -m sector_scan --help
```

---

## 5. 参数表

| 参数 | 含义 | 默认 |
|---|---|---|
| `ETF代码`(位置参数) | 目标行业 ETF | `SOXX` |
| `--hold TICKER` | 重复暴露检查标的 | 仅 SOXX 缺省 `NVDA`;其他 ETF 关闭 |
| `--no-hold` | 显式关闭重复暴露检查 | — |
| `--invest 金额` | 投入金额(算间接暴露) | `100000` |
| `--start YYYY-MM-DD` | 价格窗口起 | 近 90 天 |
| `--end YYYY-MM-DD` | 价格窗口止 | 今天 |
| `--year YYYY` | 13F 年份 | 最新季 |
| `--quarter 1-4` | 13F 季度 | 最新季 |
| `--top N` | 前 N 大成分股 | `10` |
| `--core N` | 核心 N 只 | `5` |
| `--no-brain` | 不调 DeepSeek,只出事实 | — |
| `--fixtures` | 离线用内置 SOXX 快照(0 credit) | — |
| `--html` | 输出 HTML 而非 markdown | — |
| `--out 文件` | 写入文件而非屏幕 | — |
| `--pdf 文件` | 导出 PDF(需本机 Chromium) | — |

---

## 6. 导出报告

- **markdown**(默认):直接打印到屏幕,或 `--out report.md` 存文件。
- **HTML**:`--html --out soxx.html` → 双击用浏览器打开,带集中度/机构覆盖度条形图、🧠 解读分区、免责页脚。
- **PDF**:
  - 有 Chromium:`--pdf soxx.pdf` 直接导出。
  - **没 Chromium**(如公司 WSL):先 `--html --out soxx.html`,再浏览器打开 → **Ctrl+P → 另存为 PDF**。

> 给券商演示:推荐发 **PDF**(专业、离线、带免责),或当面用浏览器打开 HTML(有图表)。

---

## 7. 示例集

```bash
# 复现文章那版(2025-12-31 口径,90 天 +78.2%)
python3 -m sector_scan SOXX --start 2026-03-23 --end 2026-06-17 --year 2025 --quarter 4

# 我持有 AVGO,投 2 万,只看前 3 大,导出网页
python3 -m sector_scan SOXX --hold AVGO --invest 20000 --top 3 --html --out avgo.html

# 快速看事实、不花 DeepSeek、当天最新数据
python3 -m sector_scan SOXX --no-brain

# 完全离线给同事演示形态
python3 -m sector_scan --fixtures --no-brain
```

---

## 8. 常见问题

| 现象 | 原因 / 解决 |
|---|---|
| `缺少 LLMQUANT_API_KEY` | 没设钥匙。先 `export`,或加 `--fixtures --no-brain` 走离线 |
| `Ticker XXX is not currently supported` | ETF 代码写错/不支持。程序会友好报错、退出码 2,不崩 |
| 顶部出现"⚠️ 覆盖提示……不适用" | 该 ETF 成分股当前映射表未覆盖(v1 只精确支持 **SOXX**);概要与价格仍有效 |
| `--fixtures` 报"仅支持 SOXX" | 离线快照只有 SOXX;其他 ETF 去掉 `--fixtures` 走实时 |
| `PDF 导出失败:未找到 Chromium` | 本机没 Chromium。用 HTML → 浏览器"打印为 PDF",或设 `CHROME_BIN` |
| `解读降级(仅出事实版)。原因:…` | AI 解读没过护栏或网络失败;**不影响数字**,报告照出,只少了 🧠 那行 |
| 数字和文章不一样 | 正常:不填日期/季度时用**最新数据**(价格实时、13F 最新季)。要复现文章见示例集 |

---

## 9. 重要说明

- **覆盖范围**:v1 标的映射表精确覆盖 **SOXX**;换任意 ETF 是后续升级(接免费的 SEC EDGAR / iShares 每日持仓,零边际成本)。
- **数据时效**:持仓来自 SEC N-PORT 监管快照(有滞后、会标 `stale`);13F 为季度末延迟披露;价格为实时。报告第 ⑦ 段会如实标注口径。
- **免责**:本工具仅供信息与研究用途,**不构成投资建议**。详见 [`docs/disclaimer.md`](docs/disclaimer.md)。
- 更多:方法论 [`docs/methodology.md`](docs/methodology.md) · 对标 [`docs/benchmark.md`](docs/benchmark.md) · 详细指南 [`docs/usage.md`](docs/usage.md)。
