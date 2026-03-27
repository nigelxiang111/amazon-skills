# SKILL: amazon-product-spy
亚马逊竞品深度解剖技能。从流量结构、用户口碑、成本利润、生命周期四维度全面剖析竞品，定位可超越的差异化机会点。

**触发关键词**：分析ASIN、帮我研究这个竞品、解剖[产品名]、[ASIN]的情况、这个产品怎么样、竞品分析

---

## 前置：ASIN提取
- 用户提供链接 → 提取B开头10位字符
- 用户提供产品名 → **【卖家精灵】** `mcp__maijiajingl__product_research` 取月销量最高结果；不可用 → `mcp__sorftime__product_search`
- 用户直接提供ASIN → 直接使用

---

## 第一阶段：快速核查

【缓存检查】asin_detail 已有则跳过。

**【卖家精灵优先】** `mcp__maijiajingl__asin_details` → 月销量/价格/BSR/评分/评论数/尺寸重量
- 不可用 → **【sorftime替代】** `mcp__sorftime__product_detail`

月销量 < 50件 → 询问用户是否继续。

---

## 第二阶段：深度采集

【缓存检查】先检查对话中已有数据。

**【卖家精灵优先】历史趋势（三选一组合）：**
- `mcp__maijiajingl__product_trend_keepa` → 价格/排名/销量历史曲线（Keepa级别）
- **不可用 →** 【以下3个并行执行】
  - `mcp__sorftime__product_trend(SalesVolume)`
  - `mcp__sorftime__product_trend(Price)`
  - `mcp__sorftime__product_trend(Rank)`

**【卖家精灵优先】评论分析（二选一）：**
- `mcp__maijiajingl__review_research` → 多维度评论分析（含买家秀、趋势）
- **不可用 →** 【以下2个并行执行】
  - `mcp__sorftime__product_reviews(Negative)`
  - `mcp__sorftime__product_reviews(Positive)`

**【卖家精灵优先】流量词（二选一，不重复调用）：**
- `mcp__maijiajingl__reverse_asin_keywords` → 自然流量词列表（含搜索量/排名/CPC）
- **不可用 →** `mcp__sorftime__product_traffic_terms` — 取前50条（关注近30天曝光词）

**【卖家精灵独有，额外价值】：**
- `mcp__maijiajingl__reverse_order_keywords` → 出单词反查（实际产生购买的词，sorftime无此数据）
- 如 reverse_asin_keywords 已获取 → 直接并行执行，不重复

**【sorftime 独有，不与卖家精灵重复】：**
- `mcp__sorftime__ali1688_similar_product` — 采购价（取25%~75%分位），卖家精灵无1688数据

---

## 第三阶段：框架分析

1. **生命周期** — product_trend_keepa / SalesVolume趋势 + Price趋势 + Rank趋势综合判断
2. **流量结构拆解**
   - 来自 `reverse_asin_keywords` → 按搜索量分：核心词 / 长尾词 / 广告词
   - 来自 `reverse_order_keywords` → 标注「高转化出单词」（与流量词区分）
3. **竞品层SWOT**
   - S：高评分/多评论/强排名/品牌认知/变体丰富
   - W：差评集中的功能缺失/变体不足/包装差/客服慢
   - O：差评改进空间/未覆盖关键词/价格带断层/出单词未充分覆盖
   - T：专利侵权可能/品牌强保护/大卖家跟进
4. **用户痛点提炼**（来自评论）— 功能性/情感性/感知性/隐性需求分类
5. **成本估算** — COGS=1688中位价×1.1÷7.2；FBA查尺寸档；佣金=售价×15%
6. **评分** — 使用 `scripts/scorer.py`（工具B），重点强化差异化空间维度

---

## 第四阶段：输出格式

```
🔍 竞品解剖：[产品名] ASIN:[X]
📅 生命周期：[阶段] | 研究价值：[高/中/低]
📊 月销X件 | $X | BSR#X | ⭐X.X (X评论) | 主力变体：[描述]
🔑 流量词TOP10（来源：卖家精灵/sorftime）：[词] X万/月 | 自然第X位
💡 出单词TOP5（仅卖家精灵）：[词] — 高转化实购词
🔲 竞品SWOT（重点标注W弱点=你的机会）
😤 用户痛点TOP3（频率+原文摘录）
👍 好评亮点（值得保留的设计点）
💰 净利润$X | 毛利率X% | ROI X%
📐 8维度评分（scorer.py输出）综合：X.X/10
🎯 差异化机会：[具体改进方向] · 建议售价$X~$X · 优先主攻关键词
📌 数据来源：卖家精灵[✓/✗] | sorftime[✓] | 1688[✓]
```
