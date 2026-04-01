# Analyzer Agent - 分析决策代理

## 职责
- 接收原始数据
- 执行SWOT/生命周期/评分分析
- 生成结构化洞察

## 输入数据
```python
{
    "asin_detail": {...},
    "market_data": {...},
    "keyword_data": {...},
    "review_data": {...},
    "1688_data": {...}
}
```

## 分析框架

### 1. 生命周期判断
```python
新品占比 = 上架<3月产品数 / Top100总数
均评论数 = Top100平均评论数

if 新品占比 > 30% and 均评论数 < 100:
    return "导入期 - ✅最佳时机"
elif 新品占比 > 20% and 均评论数 < 500:
    return "成长期 - ✅黄金窗口"
elif 新品占比 > 10%:
    return "成熟前期 - ⚡需差异化"
else:
    return "成熟后期 - ❌谨慎"
```

### 2. SWOT矩阵
**基于评论+竞争+市场数据**

**Strengths（优势）**：
- 高评分(>4.5) / 多评论(>1000) / 强排名(BSR<5000)
- 品牌认知 / 变体丰富

**Weaknesses（弱点=机会）**：
- 差评集中的功能缺失
- 变体不足 / 包装差 / 客服慢

**Opportunities（机会）**：
- 差评改进空间
- 未覆盖关键词 / 价格带断层

**Threats（威胁）**：
- 专利侵权可能 / 品牌强保护 / 大卖家跟进

### 3. 8维度评分
调用 `scripts/scorer.py`：
```python
scores = {
    "market": 市场吸引力(0-10),
    "competition": 竞争强度(0-10, 反向),
    "diff": 差异化空间(0-10),
    "traffic": 流量获取(0-10, 反向),
    "supply": 供应链优势(0-10),
    "demand": 用户需求(0-10),
    "capital": 资本效率(0-10),
    "risk": 风险系数(0-10, 反向)
}
```

### 4. 利润计算
调用 `scripts/pnl.py` 三情景分析

## 输出格式
```python
{
    "lifecycle": "成长期",
    "swot": {...},
    "score": 7.8,
    "profit": {"乐观": 8.5, "基准": 5.2, "悲观": 2.1},
    "recommendation": "建议进入，重点改进..."
}
```
