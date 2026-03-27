# SKILL: amazon-market-scout
亚马逊市场赛道侦察技能。评估指定品类或赛道是否值得进入，输出生命周期定位、SWOT、8维度评分和入场建议。

**触发关键词**：分析XX市场、XX类目好做吗、XX赛道值不值得进、评估XX品类、XX市场怎么样、帮我看看XX

---

## 前置
若用户指定分析视角（供应链/资本效率/风险/时机/差异化/流量），后续重点深化该视角；未指定则全视角各输出1~2句。

---

## 第一阶段：类目定位（快速筛选）

**【卖家精灵优先】** `mcp__maijiajingl__category_research` → 搜索产品类目列表，获取竞争数据
- 不可用 → **【sorftime替代】** `mcp__sorftime__category_search_from_product_name`

检查前3个类目（触发任一则终止）：
- 所有类目月销量 < 500 → 终止：「市场体量过小」
- 所有类目 Top3垄断 > 70% → 终止：「竞争过于集中」
- 亚马逊自营占比 > 50% → 终止：「自营主导，第三方空间极小」

通过后取**月销量最高且垄断系数最低的 TOP 2 类目**继续，记录 marketId/nodeId 备用。

---

## 第二阶段：深度数据采集

【缓存检查】已有数据则跳过对应调用。

**【卖家精灵优先】市场整体数据（二选一）：**
- `mcp__maijiajingl__market_list` → 确认细分市场并获取基础规模数据
- `mcp__maijiajingl__market_statistics` → 商品集中度 / 品牌集中度 / 需求趋势 / 价格分布 / 评分分布 / 新品上架分布
- **不可用 →** `mcp__sorftime__category_report` — 月销量/均价/评论分布/新品占比/旺季

**【sorftime 独有，与卖家精灵不重复】时序趋势（4个并行执行）：**
> 卖家精灵的 market_statistics 给的是截面数据，sorftime 的 category_trend 提供时序曲线，二者互补不重复
- `mcp__sorftime__category_trend(SalesCount)` — 近12月销量趋势
- `mcp__sorftime__category_trend(NewProductSalesAmountShare)` — 新品活跃度趋势
- `mcp__sorftime__category_trend(AmazonSalesAmountShare)` — 自营占比趋势
- `mcp__sorftime__category_trend(Top3ProductSalesAmountShare)` — 垄断系数趋势

**【卖家精灵优先】关键词数据（并行执行）：**
- `mcp__maijiajingl__keyword_mining`（输入品类核心词）→ 搜索量/CPC/竞争度/趋势
- **不可用 →** `mcp__sorftime__category_keywords` + `mcp__sorftime__keyword_detail`（TOP3核心词）

**【卖家精灵独有，可选】：**
- `mcp__maijiajingl__aba_data_research` → ABA官方品牌分析搜索词表现（sorftime无此数据）
- `mcp__maijiajingl__google_trends` → 谷歌全网搜索热度趋势
  - 不可用 → `mcp__fetch__fetch` 搜索「[品类英文名] trending 2026」→ 仍失败则跳过

---

## 第三阶段：框架分析

1. **生命周期定位** — 综合 SalesCount时序趋势 + 新品占比 + 均评论数 + 核心词趋势，对照 SKILL.md 速查表
2. **市场层SWOT**
   - S：月销量规模 / 增速趋势 / 新品机会占比 / 价格带均衡性 / ABA热词印证
   - W：Top3垄断系数 / 评论数壁垒 / 亚马逊自营威胁
   - O：价格带空白（来自 market_statistics 价格分布）/ 新兴关键词 / ABA高潜词未被充分竞争
   - T：亚马逊自营扩张趋势 / 头部品牌护城河 / 合规收紧
3. **评分** — 使用 `scripts/scorer.py`（工具B），填入8维度得分后执行

---

## 第四阶段：输出格式

```
📊 市场侦察报告：[类目]（[站点]）
📅 生命周期：[阶段] | ⏰ 入场时机：[最佳/良好/一般/不推荐]
📈 月销：X件 | 均价：$X | Top3垄断：X% | 自营：X% | 新品占比：X%
🔑 核心词：[词1]X万/月 $X.XX CPC | [词2]... | [词3]...
📊 ABA热词TOP3（如有卖家精灵数据）：[词] 点击份额X%
🌐 谷歌趋势：[上升/平稳/下降]
🔲 SWOT：✅[优势2~3条] ⚠️[劣势] 🚀[机会] ⛔[威胁]
📐 8维度评分（scorer.py输出）综合：X.X/10
🎯 [✅推荐/⚡谨慎/❌不建议] · 核心理由 · 推荐切入方向 · 重点关键词
📌 数据来源：卖家精灵[✓/✗] | sorftime[✓] | ABA[✓/✗]
```
