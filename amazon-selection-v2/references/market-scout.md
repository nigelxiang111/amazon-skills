# SKILL: amazon-market-scout
亚马逊市场赛道侦察技能。评估指定品类或赛道是否值得进入，输出生命周期定位、SWOT、8维度评分和入场建议。

**触发关键词**：分析XX市场、XX类目好做吗、XX赛道值不值得进、评估XX品类、XX市场怎么样、帮我看看XX

---

## 前置
若用户指定分析视角（供应链/资本效率/风险/时机/差异化/流量），后续重点深化该视角；未指定则全视角各输出1~2句。

---

## 第一阶段：快速筛选（满足任一则终止）

`mcp__sorftime__category_search_from_product_name` → 检查前3个类目：
- 所有类目月销量 < 500 → 终止："市场体量过小"
- 所有类目 Top3垄断 > 70% → 终止："竞争过于集中"
- 亚马逊自营占比 > 50% → 终止："自营主导，第三方空间极小"

通过后取**月销量最高且垄断系数最低的 TOP 2 类目**继续。

---

## 第二阶段：深度数据采集

【缓存检查】已有数据则跳过对应调用。

`mcp__sorftime__category_report` — 月销量/均价/评论分布/新品占比/旺季

【以下4个调用可并行执行】
- `mcp__sorftime__category_trend(SalesCount)`
- `mcp__sorftime__category_trend(NewProductSalesAmountShare)`
- `mcp__sorftime__category_trend(AmazonSalesAmountShare)`
- `mcp__sorftime__category_trend(Top3ProductSalesAmountShare)`

【以下2个调用可并行执行】
- `mcp__sorftime__category_keywords` → 获取核心词列表
- `mcp__sorftime__keyword_detail`（TOP3核心词）→ 搜索量/CPC

---

## 第三阶段：框架分析

1. **生命周期定位** — 对照 SKILL.md 速查表，综合 SalesCount趋势 + 新品占比 + 均评论数 + 核心词趋势
2. **市场层SWOT**
   - S：月销量规模 / 增速 / 新品机会占比 / 价格带均衡性
   - W：Top3垄断系数 / 评论数壁垒 / 亚马逊自营威胁
   - O：价格带空白 / 新兴关键词 / 细分人群未满足需求
   - T：亚马逊自营扩张 / 头部品牌护城河 / 合规收紧
3. **评分** — 使用 `scripts/scorer.py`（工具B），填入8维度得分后执行

---

## 第四阶段：输出格式

```
📊 市场侦察报告：[类目]（[站点]）
📅 生命周期：[阶段] | ⏰ 入场时机：[最佳/良好/一般/不推荐]
📈 月销：X件 | 均价：$X | Top3垄断：X% | 自营：X% | 新品占比：X%
🔑 核心词：[词1]X万/月 $X.XX | [词2]... | [词3]...
🔲 SWOT：✅[优势2~3条] ⚠️[劣势] 🚀[机会] ⛔[威胁]
📐 8维度评分（scorer.py输出）综合：X.X/10
🎯 [✅推荐/⚡谨慎/❌不建议] · 核心理由 · 推荐切入方向 · 重点关键词
```
