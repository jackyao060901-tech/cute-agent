# 第 2 阶 · 13F 机构层 — 发现与口径记录

> 数据:`sec_13f_list_ticker_holders`,Top10 成分股,Q4 2025(ranking_period=2025-12-31)。
> fixture:`sector_scan/fixtures/soxx_13f_2025Q4.json`(原始返回,测试零额度复用)。

## 1. Holder Count:与文章 100% 吻合 ✅

| | NVDA | AMD | MU | AVGO | AMAT | NXPI | LRCX | KLAC | TXN | ADI |
|---|---|---|---|---|---|---|---|---|---|---|
| 我们 | 779 | 668 | 644 | 747 | 645 | 469 | 624 | 584 | 642 | 590 |
| 文章 | 779 | 668 | 644 | 747 | 645 | 469 | 624 | 584 | 642 | 590 |
| Δ | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

口径:`total_holders_in_scope` = SEC Form 13F **Top 1000 机构内**持有该票的数量(不是全市场)。
**意义**:10 个全等 → 反向证明 Top10 的 ticker 映射正确、季度口径正确。Top holders 也对(Vanguard/State Street/BlackRock)。

## 2. Aggregate Value:系统性低于文章 ~1–7%,且**与 limit 无关**

实测:NVDA `limit=100` 与 `limit=1000` 的 aggregate 都是 **$2.314T**(返回行数 100→779,合计不变)
→ 接口 `aggregate_value_usd` 是**全量加总**,不是被 limit 截断。

| ticker | 我们(as-reported) | 文章 | 差异 |
|---|---|---|---|
| NVDA | $2.31T | $2.48T | ~7% |
| AMD | $192.55B | $196.30B | ~2% |
| AVGO | $964.59B | $980.41B | ~2% |
| ADI | $88.56B | $89.69B | ~1% |

**判断**:差异大小与个股涨幅正相关(NVDA 涨最多差最大)→ 最可能是
**接口给 13F 申报时点(季末)as-reported 市值,文章按更晚价格重估过**。

**处理(遵守铁律,不为对文章而篡改)**:
- 报告采用接口的 **as-reported 全量 aggregate**(有源、可复现)。
- 在 Data Quality Notes 注明:"Aggregate 13F Value = Q4 2025 申报时点市值合计,
  来源 LLMQuant `sec_13f_list_ticker_holders.aggregate_value_usd`;与第三方按更晚价格
  重估的数字可能有数个百分点差异。"

## 3. 额度
本阶共用 12 credits(Top10 ×10 + NVDA limit 验证 ×2),剩余 ~287。
后续 holder count/aggregate 用 fixture 回归,不再消耗。

## 4. 设计结论
- `limit=100` 足够(top holders 在最前,aggregate 全量不受影响)→ 省数据、不多花钱。
- 测试 `tests/test_smart_money.py` 固化"holder count 全等文章",作为回归护栏。
