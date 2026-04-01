# Profit Lab - 利润实验室模块

## 触发词
算利润、核算成本、ROI、值不值得做

## 数据需求
```python
requirements = [
    {"key": "asin_detail", "tool": "asin_details",           "params": {"asin": asin, "marketplace": marketplace}, "priority": "required"},
    {"key": "1688_price",  "tool": "ali1688_similar_product","params": {"searchName": product_name},                "priority": "optional"},
]
```

## 执行流程

### Step 1: 输入验证
```python
from core.validator import validate_asin, validate_marketplace, validate_price, validate_weight

# 如果用户提供了ASIN，验证格式
if user_asin:
    valid, result = validate_asin(user_asin)
    if not valid:
        return f"❌ {result}"

# 如果用户手动提供价格/重量，验证范围
if user_price:
    valid, msg = validate_price(float(user_price))
    if not valid:
        return f"❌ {msg}"
```

### Step 2: 调用data_collector
```python
data = agents/data_collector.collect(requirements, marketplace=marketplace)

if data["asin_detail"].get("error"):
    return "❌ 无法获取商品数据，请检查ASIN或手动输入价格/重量"
```

### Step 3: 调用pnl.py
```python
import json, subprocess

pnl_params = {
    "price":        data["asin_detail"]["price"],
    "cogs_cny":     data["1688_price"].get("median", 0),  # 可选，0表示未获取
    "weight_kg":    data["asin_detail"]["weight"],
    "fba_fee":      estimate_fba(data["asin_detail"]["weight"]),
    "monthly_target": 200
}

# 如果1688价格未获取，提示用户输入
if pnl_params["cogs_cny"] == 0:
    pnl_params["cogs_cny"] = ask_user("请输入1688采购价（人民币）：")

result = subprocess.run(
    ["python", "scripts/pnl.py", json.dumps(pnl_params), "--json"],
    capture_output=True, text=True
)
pnl_data = json.loads(result.stdout)
```

### Step 4: 输出
使用 `templates/output_formats.md` 中的 `profit_lab_template`
