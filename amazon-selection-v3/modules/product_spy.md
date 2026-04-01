# Product Spy - 竞品解剖模块

## 触发词
分析ASIN、竞品、解剖产品、这个产品怎么样

## 数据需求
```python
requirements = [
    {"key": "asin_detail",       "tool": "asin_details",           "params": {"asin": asin, "marketplace": marketplace}, "priority": "required"},
    {"key": "trend",             "tool": "product_trend_keepa",    "params": {"asin": asin, "marketplace": marketplace}, "priority": "required"},
    {"key": "reviews",           "tool": "review_research",        "params": {"asin": asin, "marketplace": marketplace}, "priority": "important"},
    {"key": "traffic_keywords",  "tool": "reverse_asin_keywords",  "params": {"asin": asin, "marketplace": marketplace}, "priority": "important"},
    {"key": "order_keywords",    "tool": "reverse_order_keywords", "params": {"asin": asin, "marketplace": marketplace}, "priority": "important"},
    {"key": "1688_price",        "tool": "ali1688_similar_product","params": {"searchName": product_name},                "priority": "optional"},
]
```

## 执行流程

### Step 1: 输入验证
```python
from core.validator import validate_asin, validate_marketplace

# 验证ASIN
valid, result = validate_asin(user_input)
if not valid:
    return f"❌ {result}\n请提供正确的ASIN（如：B08XYZ1234）"

asin = result

# 验证站点（来自router）
marketplace = router_result.get("marketplace", "US")
```

### Step 2: ASIN提取
- 用户提供链接 → 提取B开头10位
- 用户提供产品名 → 搜索取月销量最高
- 直接提供ASIN → 使用

### Step 3: 调用data_collector
```python
data = agents/data_collector.collect(requirements, marketplace=marketplace)

# 检查必需数据
if data["asin_detail"].get("error"):
    return "❌ 无法获取ASIN数据，请检查ASIN是否正确或该站点是否有此商品"
```

### Step 4: 调用analyzer
```python
insights = agents/analyzer.analyze(data, focus="竞品SWOT")
```

### Step 5: 输出
使用 `templates/output_formats.md` 中的 `product_spy_template`
