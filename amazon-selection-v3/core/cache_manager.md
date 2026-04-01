# Cache Manager - Session缓存管理

## 缓存键设计（含站点隔离）

```python
# 格式: {marketplace}:{data_type}:{identifier}
cache = {
  "US:asin_detail:B08XYZ": {detail: {...}, trend: {...}, reviews: {...}},
  "US:market:12345": {stats: {...}, top100: [...]},
  "US:keyword:折叠椅": {volume: 50000, cpc: 1.2},
  "CN:1688:折叠椅": [{price: 15, supplier: "..."}]
}
```

## 缓存规则

### 1. 调用前检查（含站点）
任何MCP调用前先查缓存：
```python
cache_key = f"{marketplace}:{data_type}:{identifier}"
if cache.has(cache_key):
    return {**cache.get(cache_key), "source": "cached"}
```

### 2. 跨模块复用
- market_scout获取的市场数据 → profit_lab可直接用
- product_spy获取的ASIN详情 → full_evaluation可直接用

### 3. 标注来源
缓存数据标注 `[cached]` 或 `[来自缓存]`

### 4. Session生命周期
对话结束自动清空，下次分析重新获取

## 可缓存数据类型

- `asin_detail` - ASIN详情（售价/尺寸/重量/类目/月销量）
- `market_data` - 类目市场数据（月销量/均价/集中度）
- `keyword_data` - 关键词搜索量/CPC
- `1688_price` - 1688采购价
- `traffic_keywords` - ASIN流量词列表
- `nodeId` - 类目节点ID

## 站点隔离说明

同一ASIN在不同站点数据不同，缓存键必须包含站点代码。
例如：`US:asin_detail:B08XYZ` 和 `DE:asin_detail:B08XYZ` 是不同缓存项。
