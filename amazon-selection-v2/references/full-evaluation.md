# SKILL: amazon-full-evaluation
亚马逊选品综合评估技能。整合市场、竞品、机会、利润四大模块全量数据，生成最终投资决策报告。

**触发关键词**：全面评估XX、给我一份完整选品报告、综合分析XX、帮我做最终决策、XX到底做不做、我要一份完整的XX分析

---

## 前置：明确参数
评估对象（ASIN或类目名）| 站点（默认US）| 卖家类型（工厂/精品/贸易，默认贸易）| 预算规模（小<$5K / 中$5K~$30K / 大>$30K）

---

## 第一阶段：全量数据采集

【缓存检查】每个调用前先检查对话中已有数据，有则跳过。
**任意单次 MCP 调用失败 → 标注"数据暂不可用"，继续执行，不中断整体流程。**

**模块A：市场层**
- `mcp__sorftime__category_search_from_product_name` → nodeId
- `mcp__sorftime__category_report`
- 【并行】`category_trend` × 4（SalesCount / NewProductSalesAmountShare / AmazonSalesAmountShare / Top3ProductSalesAmountShare）
- 【并行】`mcp__sorftime__category_keywords` + `keyword_detail`（TOP3核心词）

**模块B：产品层**（有ASIN时执行）
- `mcp__sorftime__product_report`
- 【并行】`product_trend` × 3（SalesVolume / Price / Rank）
- 【并行】`product_reviews(Negative)` + `product_reviews(Positive)` + `product_traffic_terms`

**模块C：机会层**
- 【并行】`mcp__sorftime__tiktok_similar_product`
- 【并行】Jina `mcp__jina-mcp-server__search_web` — "[产品名] patent amazon" + "[产品名] trending 2026"

**模块D：利润层**
- 【缓存检查】1688价格若已有则复用
- 【并行】`mcp__sorftime__ali1688_similar_product` + `mcp__sorftime__keyword_detail`（CPC）

---

## 第二阶段：生命周期综合定位

- 有ASIN → 以 `product_trend(SalesVolume)` 为主，category_trend 辅助
- 无ASIN → 以 `category_trend(SalesCount + NewProductSalesAmountShare)` 为主
- 数据冲突时 → 说明差异来源，给综合判断

输出：[生命周期阶段] + 入场时机评级 [S/A/B/C/D] + 窗口期约X个月

---

## 第三阶段：P&L三情景计算

使用 `scripts/pnl.py`（工具A）：
将模块D数据（1688价格/CPC/产品detail中的重量售价）填入脚本变量，写入 `/tmp/pnl.py` 执行。
Python 不可用时按脚本注释公式手算。

---

## 第四阶段：8维度评分

使用 `scripts/scorer.py`（工具B）：
将 `seller` 变量设为用户卖家类型，根据全量数据分析为每个维度打分（0~10），写入 `/tmp/score.py` 执行。
Python 不可用时加权手算：综合分 = Σ(各维度分 × 权重)。

---

## 第五阶段：综合SWOT（整合四模块，每象限≤5条）

- **S（核心优势）**：跨模块最具说服力（市场大+成本低+需求强）
- **W（致命劣势）**：最可能导致失败，按严重度排序，≤3条
- **O（即时机会）**：最值得立即行动，具体可操作
- **T（首要威胁）**：必须提前防范，具体化

---

## 第六阶段：7视角个性化建议（每条1~2句精准建议）

🏭 供应链：最大成本压缩机会在哪里
🧠 用户心理：最核心的1个未满足需求（来自差评）
💰 资本效率：基于[预算规模]建议首批库存量和启动节奏
🛡️ 风险防御：最需规避的1个风险 + 具体规避动作
⏰ 市场时机：窗口期剩余时间 + 建议决策截止时间
✨ 差异化：最可行的1个方向（SWOT机会象限+差评双重验证）
🔑 流量：最容易突破的1~2个关键词（竞争度最低+搜索量合理）

---

## 第七阶段：最终决策输出

```
🏆 综合评估报告：[产品/类目] | [站点] | [卖家类型] | 预算[规模]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 生命周期：[阶段] | 入场时机：[S/A/B/C/D] | 窗口期约X个月
📐 8维度评分（scorer.py输出）
🔲 综合SWOT（4象限各≤5条）
💡 7视角关键建议
💰 利润摘要：毛利率X% | ROI X% | 总启动$X,XXX | 月净利$XXX | 回本第X月
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 最终决策：[✅强烈推荐进入 / ⚡谨慎进入，差异化后可行 / ❌当前不建议]

  决策依据Top3：
  1. ...  2. ...  3. ...

  推荐行动计划：
  □ 本周：[具体行动]
  □ 本月：[具体行动]
  □ 3个月内：[具体行动]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**特殊规则：**
- 预算"小"（<$5K）→ 对比总启动资金 vs 用户预算缺口，给出分阶段切入建议
- 专利风险：搜索"[产品名] patent amazon"出现结果 → 在风险系数维度扣分并标注
