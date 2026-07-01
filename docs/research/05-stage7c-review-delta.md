# 第 7 阶 polish(v7c)增量复核包

> 针对上轮 3 个打包建议的修正确认。其中 #2、#3 修复的是**真实行为缺陷**
> (SOXX 恰好 0 未解析,故此前未暴露)。均附实证。数字层不变(见复核包 v2.1)。

## 修正 1:重复暴露默认(--hold)
原:全局默认 `--hold NVDA`,对任意 ETF 都做 NVDA 重复暴露检查(对非 SOXX 会误导)。
改:**智能默认** —— 仅 SOXX 缺省查 NVDA(对标文章);其他 ETF 缺省关闭;用户显式给 ticker 才查。

| 调用 | 重复暴露标的 |
|---|---|
| `sector_scan SOXX`(缺省) | NVDA |
| `sector_scan XLK`(缺省) | 关闭 |
| `sector_scan XLK --hold XOM` | XOM |
| `sector_scan SOXX --hold ""` | 关闭 |
SKILL.md 已加:仅当用户明确说'已持有 X'才传 `--hold X`,否则不假设持仓。

## 修正 2:--fixtures 仅限 SOXX(防冒充)
原缺陷:`build_scan_from_fixtures` 忽略 etf 参数、恒读 SOXX 快照 →
`XLK --fixtures` 会**静默输出 SOXX 数据冒充 XLK**。
改:非 SOXX + --fixtures 明确报错、退出码 2。实证:
```
$ python -m sector_scan XLK --fixtures --no-brain
[错误] --fixtures 仅支持 SOXX 已审计快照;XLK 请去掉 --fixtures 走实时。
退出码=2   (SOXX --fixtures 退出码=0)
```

## 修正 3:UNRESOLVED 不再静默消失
原缺陷:未解析成分股既不进 equities(集中度/矩阵),也不在别处呈现 →
**从报告里彻底消失**(对非 SOXX ETF 会漏掉持仓,无任何提示)。
改:ScanResult 记录 `unresolved_count` / `unresolved_names`;数据质量说明**显式披露**,
以 `UNRESOLVED` 文本(不依赖颜色);若 >0 则列出名单。SOXX 实际输出:
```
- 成分股 ticker 由人工核对映射表解析(已通过外部模型复核):30 只股票已解析、3 行现金、**0 只未解析 (UNRESOLVED)**;绝不臆测。
```
SKILL.md / workflow 措辞由'标红'改为'以 UNRESOLVED 文本标记 + 数据质量说明列出'。

## 回归测试(新增,固化行为)
- `test_fixtures_rejects_non_soxx`:XLK --fixtures 返回码=2
- `test_soxx_default_checks_nvda_duplicate`:SOXX 缺省含 NVDA 重复暴露($8,263)
- `test_resolution_disclosed`:数据质量说明含'X只已解析/Y只未解析(UNRESOLVED)'
- 7 组测试 + 语法编译全过。

## 请复核员确认
1. 修正 1 的默认行为是否合理、SKILL.md 指引是否足够防止 agent 乱传 --hold。
2. 修正 2 是否彻底(还有无其他'离线冒充'路径)。
3. 修正 3 的披露是否足够(unresolved 列进数据质量说明,是否还应进某个专门模块)。
4. 是否引入新副作用。
