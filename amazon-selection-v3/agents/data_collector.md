# Data Collector Agent - 数据采集代理

## 职责
- 接收数据需求列表
- 并行调用MCP工具
- 自动降级+缓存管理
- 返回标准化数据

## 输入格式

```python
requirements = [
    {"key": "asin_detail", "tool": "asin_details", "params": {"asin": "B08XYZ"}},
    {"key": "market_data", "tool": "market_statistics", "params": {"nodeId": "12345"}},
]
```

## 执行逻辑

### Step 1: 检查缓存
```python
for req in requirements:
    cache_key = f"{marketplace}:{req.key}"
    if cache.has(cache_key):
        results[req.key] = {**cache.get(cache_key), "source": "cached"}
        continue
```

### Step 2: 卖家精灵优先（带错误处理）
```python
import time

max_retries = 2
timeout = 30  # 秒

for attempt in range(max_retries + 1):
    try:
        data = mcp__卖家精灵__[req.tool](req.params, timeout=timeout)
        results[req.key] = {**data, "source": "卖家精灵"}
        cache.set(cache_key, data)
        break
    except TimeoutError:
        if attempt < max_retries:
            time.sleep(2)
            continue
        # 超时后降级
    except Exception as e:
        error_log.append(f"{req.key}: 卖家精灵失败 - {str(e)}")
        # 降级到Sorftime
```

### Step 3: Sorftime降级
```python
fallback_tool = get_sorftime_equivalent(req.tool)
if fallback_tool:
    try:
        data = mcp__sorftime__[fallback_tool](req.params, timeout=timeout)
        results[req.key] = {**data, "source": "sorftime"}
        cache.set(cache_key, data)
    except Exception as e:
        results[req.key] = {"error": f"数据暂不可用: {str(e)}", "source": "failed"}
        error_log.append(f"{req.key}: 所有数据源失败")
else:
    results[req.key] = {"error": "无可用数据源", "source": "failed"}
```

## 并行策略

**独立数据（无依赖）→ 并行调用**
```python
# 示例：ASIN详情、1688价格、TikTok热度可并行
parallel_call([
    mcp__卖家精灵__asin_details,
    mcp__sorftime__ali1688_similar_product,
    mcp__sorftime__tiktok_similar_product
])
```

**依赖数据（需nodeId/ASIN）→ 顺序调用**
```python
# 先获取nodeId
nodeId = mcp__卖家精灵__category_research(product_name)
# 再用nodeId获取市场数据
market_data = mcp__卖家精灵__market_statistics(nodeId)
```

## 返回格式

```python
{
    "asin_detail": {..., "source": "卖家精灵"},
    "market_data": {..., "source": "cached"},
    "1688_price": {..., "source": "sorftime"},
    "error_log": ["keyword_data: 数据暂不可用"],
    "completeness": "8/9 数据项成功获取"  # 数据完整度
}
```

## 部分成功策略

即使部分数据失败，也继续执行分析：
- 🔴 必需数据失败 → 中止并告知用户
- 🟡 重要数据失败 → 继续，在报告中标注"数据缺失"
- 🟢 可选数据失败 → 继续，跳过相关分析项

## 数据优先级
- 🔴 必需: `asin_detail`、`market_data`（月销量/均价）
- 🟡 重要: `traffic_keywords`、`reviews`
- 🟢 可选: `tiktok_data`、`1688_price`
