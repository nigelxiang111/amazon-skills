# SKILL: amazon-full-evaluation
亚马逊选品综合评估技能。整合市场、竞品、机会、利润四大模块全量数据，生成最终投资决策报告。

**触发关键词**：全面评估XX、给我一份完整选品报告、综合分析XX、帮我做最终决策、XX到底做不做、我要一份完整的XX分析

---

## 前置：明确参数
评估对象（ASIN或类目名）| 站点（默认US）| 卖家类型（工厂/精品/贸易，默认贸易）| 预算规模（小<$5K / 中$5K~$30K / 大>$30K）

---

## 第一阶段：全量数据采集

【缓存检查】每个调用前先检查对话中已有数据，有则跳过，不重复调用。
**任意单次 MCP 调用失败 → 标注「数据暂不可用」，继续执行，不中断整体流程。**

---

### 模块A：市场层

**【卖家精灵优先】类目定位（二选一）：**
- `mcp__maijiajingl__category_research`（品类名）→ 获取 marketId/类目节点
- 不可用 → `mcp__sorftime__category_search_from_product_name` → 获取 nodeId

**【卖家精灵优先】市场整体数据（二选一）：**
- `mcp__maijiajingl__market_list` + `mcp__maijiajingl__market_statistics` → 集中度/需求趋势/价格分布/评分分布
- 不可用 → `mcp__sorftime__category_report`

**【sorftime 独有】时序趋势（与卖家精灵截面数据互补，并行执行）：**
- `mcp__sorftime__category_trend(SalesCount)`
- `mcp__sorftime__category_trend(NewProductSalesAmountShare)`
- `mcp__sorftime__category_trend(AmazonSalesAmountShare)`
- `mcp__sorftime__category_trend(Top3ProductSalesAmountShare)`

**【卖家精灵优先】关键词（二选一）：**
- `mcp__maijiajingl__keyword_mining`（TOP3核心词）→ 搜索量/CPC/ABA热度
- 不可用 → `mcp__sorftime__category_keywords` + `mcp__sorftime__keyword_detail`（TOP3）

**【卖家精灵独有，可选】：**
- `mcp__maijiajingl__aba_data_research` → ABA官方品牌分析（月维度，sorftime无替代）

---

### 模块B：产品层（有ASIN时执行）

**【卖家精灵优先】ASIN基础数据（二选一）：**
- `mcp__maijiajingl__asin_details` → 月销量/价格/BSR/评分/评论数/尺寸
- 不可用 → `mcp__sorftime__product_report`

**【卖家精灵优先】历史趋势（二选一）：**
- `mcp__maijiajingl__product_trend_keepa` → Keepa级别历史曲线
- 不可用 → 【并行】`product_trend(SalesVolume)` + `product_trend(Price)` + `product_trend(Rank)`

**【卖家精灵优先】评论分析（二选一）：**
- `mcp__maijiajingl__review_research` → 综合评论分析
- 不可用 → 【并行】`product_reviews(Negative)` + `product_reviews(Positive)`

**【卖家精灵优先】流量词（二选一，不重复）：**
- `mcp__maijiajingl__reverse_asin_keywords` → 自然流量词+搜索量+排名
- 不可用 → `mcp__sorftime__product_traffic_terms`

**【卖家精灵独有，额外追加】：**
- `mcp__maijiajingl__reverse_order_keywords` → 出单词（高转化词，sorftime无此数据）

---

### 模块C：机会层

**【卖家精灵独有】：**
- `mcp__maijiajingl__google_trends`（产品英文名）→ 全网趋势
  - 不可用 → `mcp__fetch__fetch` 搜索「[产品名] trending 2026」→ 失败则跳过
- `mcp__maijiajingl__global_trademark_search`（产品英文名）→ 专利/商标风险排查
  - 不可用 → `mcp__fetch__fetch` 搜索「[产品名] patent amazon」→ 失败则跳过

**【sorftime 独有，不与卖家精灵重复】：**
- `mcp__sorftime__tiktok_similar_product`（英文名）→ TikTok热度验证

---

### 模块D：利润层

【缓存检查】已有数据则复用，不重复调用。

**【sorftime 独有】：**
- `mcp__sorftime__ali1688_similar_product` → 1688采购价（25%~75%分位）

**【卖家精灵优先】CPC/ACoS参考（二选一）：**
- `mcp__maijiajingl__keyword_mining`（已在模块A采集） → 复用 CPC 数据（缓存命中，不重复调用）
- 不可用 → `mcp__sorftime__keyword_detail`（核心词CPC）

---

## 第二阶段：生命周期综合定位

- 有ASIN → 以 `product_trend_keepa` / `product_trend(SalesVolume)` 为主，category_trend 辅助
- 无ASIN → 以 `market_statistics` 需求趋势 / `category_trend(SalesCount + NewProductSalesAmountShare)` 为主
- 数据冲突时 → 说明差异来源，给综合判断

输出：[生命周期阶段] + 入场时机评级 [S/A/B/C/D] + 窗口期约X个月

---

## 第三阶段：P&L三情景计算

使用 `scripts/pnl.py`（工具A）：
将模块D数据（1688价格/CPC-ACoS/产品detail中的重量售价）填入脚本变量，写入 `/tmp/pnl.py` 执行。
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
- **O（即时机会）**：最值得立即行动，具体可操作（结合 ABA词/出单词/差评改进空间）
- **T（首要威胁）**：必须提前防范，具体化（含商标/专利风险来自global_trademark_search）

---

## 第六阶段：7视角个性化建议（每条1~2句精准建议）

🏭 供应链：最大成本压缩机会在哪里
🧠 用户心理：最核心的1个未满足需求（来自评论/出单词对比分析）
💰 资本效率：基于[预算规模]建议首批库存量和启动节奏
🛡️ 风险防御：最需规避的1个风险 + 具体规避动作（含商标风险）
⏰ 市场时机：窗口期剩余时间 + 建议决策截止时间
✨ 差异化：最可行的1个方向（SWOT机会象限+差评+出单词三重验证）
🔑 流量：最容易突破的1~2个关键词（竞争度最低+搜索量合理，优先来自ABA数据）

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
📌 数据来源汇总：卖家精灵[✓/✗] | sorftime[✓] | 1688[✓] | ABA[✓/✗] | 谷歌趋势[✓/✗] | 商标库[✓/✗]
```

**特殊规则：**
- 预算「小」（<$5K）→ 对比总启动资金 vs 用户预算缺口，给出分阶段切入建议
- 商标风险：global_trademark_search 或网页搜索发现注册商标 → 在风险系数维度扣分并红色标注

---

## 第八阶段：数据保存（询问用户）

报告输出完成后，主动询问：
「✅ 分析报告已完成。是否将本次分析数据保存到本地 Excel 文件？（便于后续复盘对比）」

若用户确认：使用 `scripts/save_data.py`（工具C），将各模块数据整理后保存。
文件命名示例：`硅胶冰块托盘分析_20260327_153744.xlsx`
