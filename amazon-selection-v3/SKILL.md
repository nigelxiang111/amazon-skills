---
name: amazon-selection-v3
description: |
  Amazon选品分析v3 - 卖家精灵(优先)+Sorftime(补充)双引擎，智能路由5大场景。
  触发场景：亚马逊选品、产品分析、市场调研、利润核算、竞品研究、蓝海发现。
  关键词：分析ASIN、评估市场、算利润、找蓝海、竞品解剖、类目分析、值不值得做。
  自动识别意图并路由到对应模块，支持SWOT分析、生命周期判断、8维度评分。
---

# Amazon Selection v3 - 选品分析技能包

## 执行流程

### Step 1: 意图识别
读取 `core/router.md` 执行意图分类 → 返回 module_name

### Step 2: 加载模块
读取 `modules/{module_name}.md` 获取执行指令

### Step 3: 数据采集
调用 `agents/data_collector.md` 并行获取数据（自动缓存+降级）

### Step 4: 分析输出
调用 `agents/analyzer.md` 生成结构化报告

## 核心协议

**数据源协议**：详见 `core/data_protocol.md`
- 卖家精灵优先，Sorftime补充
- 自动降级策略

**缓存管理**：详见 `core/cache_manager.md`
- Session级智能缓存
- 跨模块数据复用

## 5大模块

| 模块 | 触发词 | 文件 |
|------|--------|------|
| 市场侦察 | 分析市场/类目/赛道 | `modules/market_scout.md` |
| 竞品解剖 | 分析ASIN/竞品 | `modules/product_spy.md` |
| 蓝海发现 | 找蓝海/推荐品类 | `modules/niche_finder.md` |
| 利润实验室 | 算利润/成本/ROI | `modules/profit_lab.md` |
| 综合评估 | 全面评估/完整报告 | `modules/full_evaluation.md` |

## 共享工具

**评分器**：`scripts/scorer.py` - 8维度加权评分
**利润计算**：`scripts/pnl.py` - 三情景P&L分析
**数据导出**：`scripts/save_data.py` - Excel保存

## 生命周期速查

| 阶段 | 新品占比 | 均评论数 | 建议 |
|------|---------|---------|------|
| 导入期 | >30% | <100 | ✅最佳 |
| 成长期 | >20% | 100-500 | ✅黄金 |
| 成熟前期 | 10-20% | 300-800 | ⚡差异化 |
| 成熟后期 | <10% | >800 | ❌谨慎 |
