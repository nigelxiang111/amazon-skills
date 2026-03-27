# SKILL: amazon-niche-finder
亚马逊蓝海机会发现技能。主动发现低竞争、高需求、处于导入期或成长期的细分类目，输出TOP3蓝海机会。

**触发关键词**：帮我找蓝海产品、推荐一个好做的品类、找机会点、有没有好做的市场、找一个新品方向、主动发现机会

---

## 前置：收集用户偏好（缺失则询问）
大品类方向（家居/电子/宠物/户外/厨房/不限）| 价格带 | 目标站点（默认US）| 卖家类型

---

## 第一阶段：类目筛选

- 用户指定品类 → `mcp__sorftime__category_tree` 获取topNodeId → `category_search_from_top_node`
- 未指定品类 → `mcp__sorftime__search_categories_broadly`

必须同时满足的筛选参数：
```
month_sales_volume_min:      1000
top3Product_sales_share_max: 0.40
amazonOwned_sales_share_max: 0.10
ratings_count_max:            500
newproduct_sales_share_min:  0.15
```
结果不足8个时放宽 `ratings_count_max` 至 800 重新搜索。
按价格偏好追加 price_min/price_max。取月销量最高的前8个候选。

---

## 第二阶段：生命周期验证（淘汰不合格）

对前8个候选调用：
- `mcp__sorftime__category_trend(SalesCount)` — 验证近6个月趋势
- `mcp__sorftime__category_trend(NewProductSalesAmountShare)` — 验证新品活跃度

淘汰条件（满足任一）：销量连续3个月下降 | 新品占比 < 10%

保留通过验证的 TOP3~5 进入深度验证。

---

## 第三阶段：深度验证（对保留类目并行执行）

【以下调用可并行执行】
- `mcp__sorftime__category_keywords` + `mcp__sorftime__keyword_detail`（<1000/月标注"细分过窄"）
- `mcp__sorftime__tiktok_similar_product` — TikTok销量验证（用英文产品名）
- Jina `mcp__jina-mcp-server__search_web` — 搜索"[产品英文名] trending 2025 2026"
- `mcp__sorftime__ali1688_similar_product` — 采购成本必须 < 售价25%，否则标注风险
- `mcp__sorftime__potential_product` — 潜力单品参考样本

---

## 第四阶段：蓝海SWOT + 输出

对TOP3建立蓝海层SWOT：
- S：低竞争/供应链成熟/搜索量上升/TikTok已有热度
- W：市场体量有限/消费者认知度低/单价偏低
- O：先发优势/关键词排名抢占/品牌建设窗口
- T：大卖家快速跟进/市场过快成熟/价格战提前

```
🌊 蓝海机会报告 | [品类] | $X~$X | [站点]
共发现X个蓝海机会，推荐TOP3：

🥇 机会一：[类目名称]
  📅 [成长期↗] 窗口约X个月
  市场：X万件/月 | 均价$X | Top3垄断X% | 新品X%
  🔑 核心词：[词]X万/月↑  📱TikTok热度：[高/中/低]
  🏭 供应链：1688货丰富，采购约¥X~¥X（占售价X%）
  🔲 SWOT + 🎯 切入建议：差异化方向/建议售价/首批备货量/优先关键词

🥈 机会二：...（同上格式）
🥉 机会三：...（同上格式）

📋 综合推荐：最优选[X] | 资金有限选[X] | 求快变现选[X]
```
