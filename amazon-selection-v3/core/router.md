# Intent Router - 意图识别与路由

## 职责
接收用户请求 → 提取站点 → 识别意图 → 返回对应模块名

## Step 0: 站点提取（新增）

在路由前先提取站点信息：
```python
# 站点关键词映射
site_map = {
    "美国": "US", "us站": "US", "亚马逊美国": "US",
    "英国": "UK", "uk站": "UK",
    "德国": "DE", "de站": "DE",
    "日本": "JP", "jp站": "JP",
    "加拿大": "CA", "ca站": "CA",
}

marketplace = "US"  # 默认美国站
for keyword, code in site_map.items():
    if keyword in query.lower():
        marketplace = code
        break

# 直接包含站点代码
for code in ["US", "UK", "DE", "FR", "ES", "IT", "JP", "CA", "MX", "AU"]:
    if code in query.upper():
        marketplace = code
        break
```

## 路由规则

### 精确匹配（confidence=1.0）
- **包含ASIN/B0开头10位** → `product_spy`
- **包含"算利润/成本/ROI"** → `profit_lab`
- **包含"全面/综合/完整报告/最终决策"** → `full_evaluation`

### 语义匹配（confidence=0.8-0.95）

**market_scout** 触发词：
- 市场、类目、赛道、品类、好做吗、值不值得进入
- 评估XX市场、XX类目怎么样

**product_spy** 触发词：
- 竞品、解剖、分析产品、这个产品
- ASIN、链接分析

**niche_finder** 触发词：
- 蓝海、机会、推荐、找品、新品方向
- 帮我找、有什么好做的

**profit_lab** 触发词：
- 利润、成本、核算、ROI、值不值得做
- 算一下、帮我算

**full_evaluation** 触发词：
- 全面评估、综合分析、完整报告
- 最终决策、深度分析

## 处理逻辑

```python
def route(query: str) -> tuple[str, float, str]:
    """返回 (module_name, confidence, marketplace)"""
    
    # 提取站点
    marketplace = extract_marketplace(query)
    
    # 精确匹配
    if re.search(r'B0[A-Z0-9]{8}', query.upper()):
        return "product_spy", 1.0, marketplace

    if any(w in query for w in ["算", "利润", "成本", "ROI"]):
        return "profit_lab", 1.0, marketplace

    if any(w in query for w in ["全面", "综合", "完整", "最终"]):
        return "full_evaluation", 1.0, marketplace

    # 语义匹配
    scores = {module: semantic_match(query, keywords) for module, keywords in intent_map}
    best_match = max(scores, key=scores.get)
    best_score = scores[best_match]

    if best_score >= 0.8:
        return best_match, best_score, marketplace
    
    # 多意图处理
    return None, best_score, marketplace
```

## 多意图处理

当 confidence < 0.8 或多个意图得分接近时，展示带置信度的选项：

```
我理解您可能想要：
① 分析市场整体（置信度: 72%）
② 研究特定竞品（置信度: 65%）
③ 找新品机会（置信度: 45%）
④ 算利润

请选择或直接描述您的需求：
```

## 返回格式

```python
{
    "module": "product_spy",
    "confidence": 0.95,
    "marketplace": "US",
    "extracted_asin": "B08XYZ123A"  # 如有
}
```
