# Niche Finder - 蓝海发现模块

## 触发词
找蓝海、推荐品类、找机会、新品方向

## 数据需求
```python
requirements = [
    {"key": "potential_products", "tool": "potential_product",                  "params": {"marketplace": marketplace},                    "priority": "required"},
    {"key": "category_list",      "tool": "category_search_from_product_name",  "params": {"searchName": keyword, "marketplace": marketplace}, "priority": "important"},
]
```

## 执行流程

### Step 1: 输入验证
```python
marketplace = router_result.get("marketplace", "US")

# 如果用户提供了关键词，验证
if user_keyword:
    from core.validator import validate_product_name
    valid, keyword = validate_product_name(user_keyword)
    if not valid:
        keyword = None  # 无关键词时做全类目蓝海搜索
```

### Step 2: 调用data_collector
```python
data = agents/data_collector.collect(requirements, marketplace=marketplace)

if data["potential_products"].get("error"):
    return "❌ 无法获取潜力产品数据，请稍后重试"
```

### Step 3: 筛选条件
- 月销量: 500-5000件（中等规模，竞争不过激）
- 新品占比: >20%（市场仍在成长）
- 竞争度: 中低（Top3垄断率 <40%）
- Amazon自营占比: <20%（避免直接竞争）

### Step 4: 输出
使用 `templates/output_formats.md` 中的 `niche_finder_template`
