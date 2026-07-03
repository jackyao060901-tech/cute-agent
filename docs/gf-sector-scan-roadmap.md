# gf-sector-scan 升级规划(Roadmap)

> 存放地:cute-agent(私有,**非 student**),避免客户翻到内部规划。
> gf-sector-scan 仓库我(Claude)只读、推不动 → 代码改动做成本地提交 + 打包,jack 醒后上传 student。
> 最后更新:2026-07-03(夜间自动执行前）。

---

## ✅ 已完成(Tier 1)—— 现状基线

| 项 | 内容 |
|---|---|
| 自建 SEC EDGAR 13F Top1000 pipeline | 按 CUSIP 计数、CIK latest-effective 去重、三口径(含期权/普通股/只期权),对账文章 ≤0.9% |
| 泛化 16 只 ETF(全行业) | N-PORT 抽成分股 + OpenFIGI/13F 解析 ticker |
| 主要机构名 | 每票前 N 大机构(SEC 申报人,确定性) |
| UNRESOLVED 68→6 | 大票用 SEC 13F 自带 ticker 补全 |
| 13F 证据链 + 三口径对账表 | Markdown / HTML / PDF 三格式 |
| 可选原始 XML 审计 | `--download-13f-xml`,含 Vanguard/BlackRock/State Street 样本 |

已交付季度:仅 **2025Q4**。已交付 ETF:16 只(SOXX/SMH/XLK/QQQ/IGV/IBB/XLF/XLE/XLV/XLY/XLP/XLI/XLU/XLB/XLRE/XLC)。

---

## 🔴 P0 · 补现有报告缺口(优先,先让报告"无空格")

| 项目 | 做什么 / 答什么 | 数据/代码 | 成本 | 价值 | 铁律风险 | 依赖 |
|---|---|---|---|---|---|---|
| **P0-1 AUM + 发行方** | ②快照两空格:AUM=N-PORT `NET_ASSETS`、发行方=`REGISTRANT_NAME`,挂 source+date | 数据+渲染小改 | 机时~15min,code S | 中高 | 无(确定性有来源) | 已验证可抽 |
| **P0-2 「合计13F市值」差异说明** | 查清 0.9–6.7% 差异是估值日还是口径,把话说死 | 分析 | code S | 中 | 无 | — |
| **P0-3 最后6只UNRESOLVED** | Thomson Reuters/Amcor/CureVac 等,edgartools 公司查 ISIN 补 ticker | 数据 | 机时~10min | 低 | 无(补不上仍标UNRESOLVED) | — |

## 🟠 P1 · 多季度 + 环比(北极星:从"快照"到"聪明钱动向")

| 项目 | 做什么 / 答什么 | 数据/代码 | 成本 | 价值 | 依赖 |
|---|---|---|---|---|---|
| **P1-1 多季度数据** | 补 2025Q3/Q2 fixture(`--quarter` 已就绪,仅缺数据) | 数据 | ~50min/季 机时,零代码 | 高 | N-PORT历史包 |
| **P1-2 环比趋势 ΔHolders** | NVDA 760→773(+13,加仓);矩阵加趋势列 | code M | **最高** | 依赖 P1-1 |

## 🟡 P2 · 功能 / 体验

| 项目 | 答什么 | 成本 | 价值 |
|---|---|---|---|
| P2-1 单问模式 `--only/ask` | "只想知道 NVDA 在 SMH 被多少机构持有" | code M | 高 |
| P2-2 多 ETF 对比 | "XLK 和 QQQ 重叠多少" | code M | 高 |
| P2-3 CSV/XLSX 导出 | 进 Excel/Bloomberg | code S-M | 中 |
| P2-4 组合级重复暴露 | 持有多票的整体重复 | code M | 中 |
| P2-5 英文版报告 | 境外券商 | code S | 中 |
| P2-6 更多 ETF(>16) | 更多行业/主题 | 机时 | 中 |

## 🔧 P3 · 维护 / 技术债

| 项目 | 说明 | 成本 |
|---|---|---|
| P3-1 XML 审计瘦身(导师提的) | 默认只出 accession_index.csv(带SEC链接),XML 改 `--save-xml` 才落地 | code S |
| P3-2 清理 779 旧文件 | soxx_13f_2025Q4.json 现只剩单测用,定位标清/归档 | code S |
| P3-3 图表可视化 | 集中度/趋势加图,PDF 更像研报 | code M |

---

## 执行节奏(建议)
**P0-1 → P0-2/3 → P1-1(生成2025Q3)→ P1-2(环比)→ P2 按需 → P3 有空清。**

## 夜间自动执行记录
- 见本仓库同分支的提交历史 + gf-sector-scan 本地 `final` 分支的提交(醒后打包上传 student)。
