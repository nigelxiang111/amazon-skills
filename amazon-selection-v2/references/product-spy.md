# SKILL: amazon-product-spy
亚马逊竞品深度解剖技能。从流量结构、用户口碑、成本利润、生命周期四维度全面剖析竞品，定位可超越的差异化机会点。

**触发关键词**：分析ASIN、帮我研究这个竞品、解剖[产品名]、[ASIN]的情况、这个产品怎么样、竞品分析

---

## 前置：ASIN提取
- 用户提供链接 → 提取B开头10位字符
- 用户提供产品名 → `mcp__sorftime__product_search` 取月销量最高结果
- 用户直接提供ASIN → 直接使用

---

## 第一阶段：快速核查

【缓存检查】product_detail 已有则跳过。
`mcp__sorftime__product_detail` → 月销量 < 50件则询问用户是否继续。

---

## 第二阶段：深度采集

【缓存检查】先检查对话中已有数据。

`mcp__sorftime__product_report` — 月销量/销额/BSR/价格/评分/评论数

【以下5个调用可并行执行】
- `mcp__sorftime__product_trend(SalesVolume)`
- `mcp__sorftime__product_trend(Price)`
- `mcp__sorftime__product_trend(Rank)`
- `mcp__sorftime__product_reviews(Negative)`
- `mcp__sorftime__product_reviews(Positive)`

`mcp__sorftime__product_traffic_terms` — 取前50条流量词（关注近30天曝光词）
`mcp__sorftime__ali1688_similar_product` — 采购价（取25%~75%分位）

---

## 第三阶段：框架分析

1. **生命周期** — SalesVolume趋势 + Price趋势 + Rank趋势综合判断
2. **流量结构拆解** — 自然搜索词 / 广告词 / 长尾词 三类分类
3. **竞品层SWOT**
   - S：高评分/多评论/强排名/品牌认知/变体丰富
   - W：差评集中的功能缺失/变体不足/包装差/客服慢
   - O：差评改进空间/未覆盖关键词/价格带断层
   - T：专利侵权可能/品牌强保护/大卖家跟进
4. **用户痛点提炼**（来自差评）— 功能性/情感性/感知性/隐性需求分类
5. **成本估算** — COGS=1688中位价×1.1÷7.2；FBA查尺寸档；佣金=售价×15%
6. **评分** — 使用 `scripts/scorer.py`（工具B），重点强化差异化空间维度

---

## 第四阶段：输出格式

```
🔍 竞品解剖：[产品名] ASIN:[X]
📅 生命周期：[阶段] | 研究价值：[高/中/低]
📊 月销X件 | $X | BSR#X | ⭐X.X (X评论) | 主力变体：[描述]
🔑 流量词TOP10：[词] X万/月 | 自然第X位 / 广告词
🔲 竞品SWOT（重点标注W弱点=你的机会）
😤 用户痛点TOP3（频率+原文摘录）
👍 好评亮点（值得保留的设计点）
💰 净利润$X | 毛利率X% | ROI X%
📐 8维度评分（scorer.py输出）综合：X.X/10
🎯 差异化机会：[具体改进方向] · 建议售价$X~$X · 优先主攻关键词
```
