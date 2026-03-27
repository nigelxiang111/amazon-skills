# SKILL: amazon-niche-finder
亚马逊蓝海机会发现技能。主动发现低竞争、高需求、处于导入期或成长期的细分类目，输出TOP3蓝海机会。

**触发关键词**：帮我找蓝海产品、推荐一个好做的品类、找机会点、有没有好做的市场、找一个新品方向、主动发现机会

---

## 前置：收集用户偏好（缺失则询问）
大品类方向（家居/电子/宠物/户外/厨房/不限）| 价格带 | 目标站点（默认US）| 卖家类型

---

## 第一阶段：类目筛选

**【卖家精灵优先】：**
- 用户指定品类 → `mcp__maijiajingl__category_research`（按品类名搜索，获取市场列表）
- 未指定品类 → `mcp__maijiajingl__market_list`（获取大盘细分市场列表）
- **不可用 →** 【sorftime替代】：
  - 用户指定品类 → `mcp__sorftime__category_tree` 获取topNodeId → `category_search_from_top_node`
  - 未指定品类 → `mcp__sorftime__search_categories_broadly`

**筛选参数（无论来自哪个数据源，必须同时满足）：**
```
月销量:              ≥ 1000
Top3垄断系数:        ≤ 40%
亚马逊自营占比:      ≤ 10%
均评论数:            ≤ 500
新品销量占比:        ≥ 15%
```
结果不足8个时放宽「均评论数」至 800 重新搜索。
按价格偏好追加 price_min/price_max。取月销量最高的前8个候选。

---

## 第二阶段：生命周期验证（淘汰不合格）

**【卖家精灵优先】：**
- `mcp__maijiajingl__market_statistics`（对应market/nodeId）→ 检查「商品需求趋势」字段
- **不可用 →** 【sorftime替代，并行执行】：
  - `mcp__sorftime__category_trend(SalesCount)` — 验证近6个月趋势
  - `mcp__sorftime__category_trend(NewProductSalesAmountShare)` — 验证新品活跃度

淘汰条件（满足任一）：销量连续3个月下降 | 新品占比 < 10%

保留通过验证的 TOP3~5 进入深度验证。

---

## 第三阶段：深度验证（对保留类目并行执行）

以下各项针对不同数据维度，来自不同数据源，可全部并行执行：

**【卖家精灵优先】关键词验证：**
- `mcp__maijiajingl__keyword_mining`（品类核心英文词）→ 搜索量/CPC/竞争度
  - 搜索量 < 1000/月 → 标注「细分过窄」
  - 不可用 → `mcp__sorftime__category_keywords` + `mcp__sorftime__keyword_detail`

**【卖家精灵独有】趋势与合规：**
- `mcp__maijiajingl__google_trends`（品类英文词）→ 全网搜索热度趋势
  - 不可用 → `mcp__fetch__fetch` 搜索「[产品英文名] trending 2026」→ 仍失败则跳过，标注「站外趋势暂不可用」
- `mcp__maijiajingl__global_trademark_search`（品类英文词）→ 商标风险排查
  - 不可用 → `mcp__fetch__fetch` 搜索「[产品名] trademark amazon」→ 失败则跳过

**【sorftime 独有，不与卖家精灵重复】：**
- `mcp__sorftime__tiktok_similar_product`（英文产品名）→ TikTok热度验证（卖家精灵无TikTok数据）
- `mcp__sorftime__ali1688_similar_product` → 采购成本必须 < 售价25%，否则标注风险（卖家精灵无1688数据）
- `mcp__sorftime__potential_product` → 潜力单品参考样本（卖家精灵无此功能）

---

## 第四阶段：蓝海SWOT + 输出

对TOP3建立蓝海层SWOT：
- S：低竞争/供应链成熟/搜索量上升/TikTok已有热度/谷歌趋势上升
- W：市场体量有限/消费者认知度低/单价偏低
- O：先发优势/关键词排名抢占/品牌建设窗口/ABA词未充分竞争
- T：大卖家快速跟进/市场过快成熟/价格战提前/商标注册障碍

```
🌊 蓝海机会报告 | [品类] | $X~$X | [站点]
共发现X个蓝海机会，推荐TOP3：

🥇 机会一：[类目名称]
  📅 [成长期↗] 窗口约X个月
  市场：X万件/月 | 均价$X | Top3垄断X% | 新品X%
  🔑 核心词：[词]X万/月↑（卖家精灵/sorftime）
  🌐 谷歌趋势：[上升/平稳]  📱TikTok热度：[高/中/低]
  🏭 供应链：1688货丰富，采购约¥X~¥X（占售价X%）
  🛡️ 商标风险：[无/低/注意-XX品牌已注册]
  🔲 SWOT + 🎯 切入建议：差异化方向/建议售价/首批备货量/优先关键词

🥈 机会二：...（同上格式）
🥉 机会三：...（同上格式）

📋 综合推荐：最优选[X] | 资金有限选[X] | 求快变现选[X]
📌 数据来源：卖家精灵[✓/✗] | sorftime[✓] | 谷歌趋势[✓/✗]
```
