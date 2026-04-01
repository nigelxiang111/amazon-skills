# Data Protocol - 数据源协议

## 三层优先级

```
Layer 1: Session缓存（已有数据直接复用）
Layer 2: 卖家精灵（数据质量优先）
Layer 3: Sorftime（补充+独有数据）
```

## 核心原则

1. **缓存优先**：对话中已有该数据 → 直接复用，不重复调用
2. **卖家精灵优先**：有对应工具 → 先用卖家精灵
3. **Sorftime补充**：卖家精灵无此功能/失败/返回空 → Sorftime补充，标注`[sorftime数据]`
4. **不重复采集**：同一数据维度只从一个源获取

## 工具映射表

| 数据维度 | 卖家精灵（优先）| Sorftime（备用）| 备注 |
|---------|---------------|----------------|------|
| ASIN详情+月销量 | `asin_details` | `product_detail` + `product_report` | 二选一 |
| ASIN历史趋势 | `product_trend_keepa` | `product_trend` | 二选一 |
| ASIN流量词 | `reverse_asin_keywords` | `product_traffic_terms` | 二选一 |
| ASIN出单词 | `reverse_order_keywords` | - | 卖家精灵独有 |
| ASIN评论 | `review_research` | `product_reviews` | 二选一 |
| 关键词搜索量 | `keyword_mining` | `keyword_detail` | 二选一 |
| 关键词扩展 | `expand_traffic_keywords` | `keyword_extends` | 二选一 |
| ABA官方数据 | `aba_data_research` | - | 卖家精灵独有 |
| 类目市场数据 | `market_list` + `market_statistics` | `category_report` | 二选一 |
| 类目筛选 | `category_research` | `category_search_from_product_name` | 二选一 |
| 类目趋势 | - | `category_trend` | Sorftime独有 |
| 竞品列表 | `competitor_research` | `product_search` | 二选一 |
| 1688采购价 | - | `ali1688_similar_product` | Sorftime独有 |
| TikTok热度 | - | `tiktok_similar_product` | Sorftime独有 |

## 调用格式

**卖家精灵**：`mcp__卖家精灵__工具名`
**Sorftime**：`mcp__sorftime__工具名`

## 降级策略

```
卖家精灵失败 → 自动切换Sorftime → 标注[sorftime数据]
Sorftime失败 → 标注"数据暂不可用" → 继续流程
```
