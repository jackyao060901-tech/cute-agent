# cute-agent — 工作准则 (Working Principles)

> 本文件是与 jack 协作的最高准则。**每次写代码前,先通读这三条铁律。** 不得违背。
> 它存在的意义之一就是"不靠记忆、不会忘"——上下文被压缩也丢不了。

---

## 三条铁律 (Three Standing Rules)

### 第一句 · 中心与质量
- **中心**:用 agent 做出 skill,满足**量化投资**需求(SOXX 的 Sector Smart Money Scan 是第一个)。
- 一切产出必须保证四项:**准确性 (Accuracy) · 可读性 (Readability) · 对方(券商)认可度 (Recognition) · 真实性 (Authenticity)**。
- **反复检查,杜绝幻觉**:
  - 数字**不经 LLM 之手**——全部确定性计算,LLM 只写文字解读。
  - 每个数据都挂 `source + as_of_date`;拿不到就显式标"缺失",**绝不用模型记忆补**。
  - 事实与解读视觉分区,不混淆。

### 第二句 · 节奏
- **慢慢来,一步一步,要稳、要好。** 不追求一次性做完。
- 先搭第一版,再**反复迭代升级**。每一台阶:做扎实 → 验给 jack 看 → 确认后再走下一步。
- **拿不准就问 jack,不自负。** jack 会用其他大模型交叉验证我的产出。

### 第三句 · 可回退 (Reversibility)
- 后续更新的**重要操作必须可回退 (be able to reverse)**。**绝不能毁掉上一版。**
- 做法:
  - 每完成一个台阶就 **git 提交一次**,commit message 清晰。
  - 大改动前,先确保上一版已提交 / 可恢复;**不直接覆盖能用的版本**。
  - 万一新版"崩盘",必须能**一键回到上一版**。

---

## 协作约定 (Conventions)
- **开发分支**:`claude/kai-gong-kai-gong-kai-gong-3n5cvv`
- **语言**:对 jack 输出中文;代码内英文术语 + 中文注释。
- **API Key**:jack 同意 Key 可直接进仓库(仓库将设为 **private**)。
  即便如此,**代码仍从环境变量读取,不在源码里硬编码**;Key 集中放配置文件,便于轮换。
  ⚠️ 在仓库**确认为 private 之前,不把 Key push 到远端**,以免公开泄露。
- **两把钥匙**:DeepSeek Key = 大脑(写解读);LLMQuant Data Key = 数据(持仓/13F/价格)。

---

## 进度台阶 (Roadmap — 每阶独立可验证)
1. **持仓 + 标的解析**:拉真实 SOXX 全持仓,`holding_name/cusip/isin → ticker` 全部解析正确(进行中)
2. 13F 层:逐成分股 holder count / aggregate / top holders
3. 价格层:90 天窗口,确定性算收益
4. 计算层:集中度分层、重复暴露真计算(单元测试)
5. 渲染层:8 模块中文 dashboard(只放事实)
6. DeepSeek 大脑:文字解读 + 防幻觉护栏
7. 打包:CLI 工具 → 封装成 Claude Code skill
8. 质量/合规:方法论文档、免责、HTML/PDF、对标文章

> 详细调研见 `docs/research/00-preparation-dossier.md`。
