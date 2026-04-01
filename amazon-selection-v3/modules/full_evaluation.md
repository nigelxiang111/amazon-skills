# Full Evaluation - 综合评估模块

## 触发词
全面评估、综合分析、完整报告、最终决策

## 数据依赖图
```
product_name/asin
    ├── asin → asin_detail (required)
    │         └── product_name → 1688_price (optional)
    └── product_name → nodeId (required)
                       └── nodeId → market_data (required)
                                    category_trend (important)
```

## 数据需求（按依赖顺序）
```python
# 阶段1: 并行获取独立数据
phase1 = [
    {"key": "asin_detail",  "tool": "asin_details",          "params": {"asin": asin, "marketplace": marketplace},           "priority": "required"},
    {"key": "nodeId",       "tool": "category_research",     "params": {"searchName": product_name, "marketplace": marketplace}, "priority": "required"},
]

# 阶段2: 依赖phase1结果，并行获取
phase2 = [
    {"key": "market_data",       "tool": "market_statistics",         "params": {"nodeId": nodeId, "marketplace": marketplace},  "priority": "required"},
    {"key": "reviews",           "tool": "review_research",           "params": {"asin": asin, "marketplace": marketplace},      "priority": "important"},
    {"key": "traffic_keywords",  "tool": "reverse_asin_keywords",     "params": {"asin": asin, "marketplace": marketplace},      "priority": "important"},
    {"key": "1688_price",        "tool": "ali1688_similar_product",   "params": {"searchName": product_name},                    "priority": "optional"},
    {"key": "category_trend",    "tool": "category_trend",            "params": {"nodeId": nodeId, "marketplace": marketplace},  "priority": "important"},
]
```

## 执行流程

### Step 1: 输入验证
```python
from core.validator import validate_asin, validate_product_name

# 验证ASIN（如提供）
if user_asin:
    valid, asin = validate_asin(user_asin)
    if not valid:
        return f"❌ {asin}"

marketplace = router_result.get("marketplace", "US")
```

### Step 2: 调用data_collector（两阶段）
```python
# 阶段1
phase1_data = data_collector.collect(phase1, marketplace=marketplace)

# 检查必需数据
if phase1_data["asin_detail"].get("error") or phase1_data["nodeId"].get("error"):
    return "❌ 无法获取基础数据，请检查ASIN或产品名称"

# 提取依赖值
nodeId = phase1_data["nodeId"]["value"]

# 阶段2（并行）
phase2_data = data_collector.collect(phase2, marketplace=marketplace)
data = {**phase1_data, **phase2_data}
```

### Step 3: 调用analyzer（全面分析）
```python
insights = agents/analyzer.analyze(data, focus="综合评估")
```

### Step 4: 调用scorer.py
```python
import json, subprocess
score_result = subprocess.run(
    ["python", "scripts/scorer.py", json.dumps({"seller": seller_type, "scores": insights["scores"]}), "--json"],
    capture_output=True, text=True
)
score_data = json.loads(score_result.stdout)
```

### Step 5: 输出
使用 `templates/output_formats.md` 中的 `full_evaluation_template`

### Step 6: 询问保存
「是否将分析数据保存到本地Excel？」
如确认，调用 `scripts/save_data.py`
