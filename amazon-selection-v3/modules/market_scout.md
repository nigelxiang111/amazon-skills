# Market Scout - 市场侦察模块

## 触发词
分析市场、类目好做吗、赛道、评估品类

## 数据需求
```python
requirements = [
    {"key": "nodeId",        "tool": "category_research", "params": {"searchName": product_name, "marketplace": marketplace}, "priority": "required"},
    {"key": "market_data",   "tool": "market_statistics", "params": {"nodeId": nodeId, "marketplace": marketplace},           "priority": "required"},
    {"key": "category_trend","tool": "category_trend",    "params": {"nodeId": nodeId, "marketplace": marketplace},           "priority": "important"},
]
```

## 执行流程

### Step 1: 输入验证
```python
from core.validator import validate_product_name

valid, result = validate_product_name(user_input)
if not valid:
    return f"❌ {result}"

product_name = result
marketplace = router_result.get("marketplace", "US")
```

### Step 2: 获取类目ID（依赖步骤，必须先执行）
```python
nodeId_data = data_collector.collect([
    {"key": "nodeId", "tool": "category_research", "params": {"searchName": product_name, "marketplace": marketplace}}
])

if nodeId_data["nodeId"].get("error"):
    return f"❌ 未找到'{product_name}'相关类目，请尝试更精确的品类名称"

nodeId = nodeId_data["nodeId"]["value"]
```

### Step 3: 并行获取市场数据
```python
data = data_collector.collect([
    {"key": "market_data",    ...},
    {"key": "category_trend", ...},
], marketplace=marketplace)
```

### Step 4: 调用analyzer
```python
insights = agents/analyzer.analyze(data, focus="市场生命周期")
```

### Step 5: 输出
使用 `templates/output_formats.md` 中的 `market_scout_template`
