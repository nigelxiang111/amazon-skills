---
name: amazon-selection-v2
description: |
  Amazon 亚马逊选品分析技能包 v2.0，整合卖家精灵（优先）、Sorftime（补充）、1688 三大数据源。
  包含 5 个专项技能，自动识别用户意图并路由到对应技能：
  · 市场侦察 (amazon-market-scout): 分析XX市场、XX类目好做吗、XX赛道值不值得进、评估XX品类
  · 竞品解剖 (amazon-product-spy): 分析ASIN、帮我研究这个竞品、解剖[产品名]、竞品分析
  · 蓝海发现 (amazon-niche-finder): 帮我找蓝海产品、推荐好做的品类、找机会点、找新品方向
  · 利润实验室 (amazon-profit-lab): 帮我算利润、核算成本、算一下ROI、利润分析、值不值得做
  · 综合评估 (amazon-full-evaluation): 全面评估XX、完整选品报告、综合分析、帮我做最终决策

  遇到任何亚马逊选品、产品分析、市场调研、利润核算相关请求时必须激活此技能。
---

# Amazon 选品分析技能包 v2.0
> 卖家精灵(优先) · Sorftime(补充) · 1688(货源) · Fetch(网页) — 5技能 · SWOT · 生命周期 · 8维度评分

## 意图路由

收到用户请求后，先匹配技能，再读取对应 references/ 文件获取完整指令：

| 用户意图关键词 | 技能 | 读取文件 |
|---|---|---|
| 分析市场 / 品类好做吗 / 赛道 / 评估类目 | market-scout | `references/market-scout.md` |
| 分析ASIN / 竞品 / 解剖产品 / 这个产品怎么样 | product-spy | `references/product-spy.md` |
| 找蓝海 / 推荐品类 / 找机会 / 新品方向 | niche-finder | `references/niche-finder.md` |
| 算利润 / 核算成本 / ROI / 值不值得做 | profit-lab | `references/profit-lab.md` |
| 全面评估 / 完整报告 / 综合分析 / 最终决策 | full-evaluation | `references/full-evaluation.md` |

> 意图不明确时，询问用户：「您是想分析市场整体情况、还是研究特定竞品、还是找新品机会？」

---

## 数据源优先级协议（所有技能强制遵守）

### 四条核心原则
1. **缓存优先**：对话中已有该数据 → 直接复用，任何 MCP 都不重复调用
2. **卖家精灵优先**：有对应工具 → 先用卖家精灵（数据质量与深度更优）
3. **sorftime补充**：卖家精灵无此功能 / 调用失败 / 返回空 → sorftime补充，标注 `[sorftime数据]`
4. **不重复采集**：同一数据维度只从一个源获取，不并行调用两个源拿同类数据

### 工具映射速查表

| 数据维度 | 卖家精灵（优先）| sorftime（备用/补充）| 备注 |
|---|---|---|---|
| ASIN详情+月销量 | `asin_details` | `product_detail` + `product_report` | 二选一 |
| ASIN历史趋势 | `product_trend_keepa` | `product_trend(SalesVolume/Price/Rank)` | 二选一 |
| ASIN流量词(自然) | `reverse_asin_keywords` | `product_traffic_terms` | 二选一 |
| ASIN出单词 | `reverse_order_keywords` | — | 卖家精灵唯一 |
| ASIN评论分析 | `review_research` | `product_reviews(Negative/Positive)` | 二选一 |
| 关键词搜索量/CPC | `keyword_mining` | `keyword_detail` | 二选一 |
| 关键词长尾扩展 | `expand_traffic_keywords` | `keyword_extends` | 二选一 |
| ABA官方搜索数据 | `aba_data_research` | — | 卖家精灵唯一 |
| 谷歌趋势 | `google_trends` | `fetch`网页搜索 | 二选一，fetch失败则跳过 |
| 类目市场整体数据 | `market_list` + `market_statistics` | `category_report` | 二选一 |
| 类目快速筛选 | `category_research` | `category_search_from_product_name` | 二选一 |
| 类目时序趋势 | — | `category_trend` | sorftime唯一 |
| 竞品筛选列表 | `competitor_research` | `product_search` | 二选一 |
| 商标/专利检查 | `global_trademark_search` | `fetch`网页搜索 | 二选一，fetch失败则跳过 |
| 1688采购价 | — | `ali1688_similar_product` | sorftime唯一 |
| TikTok热度 | — | `tiktok_similar_product` | sorftime唯一 |
| 潜力单品挖掘 | — | `potential_product` | sorftime唯一 |

> 调用卖家精灵工具统一加前缀 `mcp__maijiajingl__`，例如 `mcp__maijiajingl__asin_details`

---

## 共享协议（所有技能强制遵守）

### 生命周期速查表
| 阶段 | 新品占比 | 均评论数 | 入场建议 |
|------|---------|---------|---------|
| 导入期 | >30% | <100 | ✅最佳时机 |
| 成长期 | >20% | 100~500 | ✅黄金窗口 |
| 成熟前期 | 10~20% | 300~800 | ⚡需差异化 |
| 成熟后期 | <10% | >800 | ❌谨慎 |
| 衰退期 | <5% | 停增长 | ❌不进入 |

### Session 缓存协议
每次 MCP 调用前，**先检查当前对话中是否已有该数据**，有则直接复用，不重复调用：
- `nodeId` / `marketId` — category_research 或 category_search 返回值
- `asin_detail` — ASIN详情（售价/尺寸/重量/类目/月销量），任一来源均可复用
- `market_data` — 类目市场数据（月销量/均价/集中度），任一来源均可复用
- `keyword_data` — 关键词搜索量/CPC（来自卖家精灵或sorftime均可复用）
- `1688_price` — ali1688_similar_product 返回值
- `traffic_keywords` — ASIN流量词列表，任一来源均可复用

### 数据降级规则
- **卖家精灵** 不可用/返回空 → 切换 sorftime 对应工具，标注 `[sorftime数据]`
- **sorftime** 不可用 → 标注「数据暂不可用」，不中断流程
- **Jina** 不可用 → 先用 `mcp__fetch__fetch` 重试；仍失败则跳过，标注「站外趋势暂不可用」
- 1688货源 < 3家 → 标注「⚠️ 供应链风险：货源稀缺」
- Python 不可用 → 按 scripts/ 中的注释公式手动计算，结果完全等价

---

## 共享计算工具

### 工具A：P&L 三情景计算器
用于 profit-lab 和 full-evaluation。脚本路径：`scripts/pnl.py`

**使用方法：**
1. 将 API 真实数据填入脚本顶部变量（price / cogs_cny / weight_kg / fba_fee / acos_base / monthly_target）
2. 写入 `/tmp/pnl.py` 并执行 `python3 /tmp/pnl.py`
3. 将输出结果纳入报告

FBA费用参考（无法获取时按此估算）：
- 小号标准 ≤4oz：$3.22 | 中号标准 ≤1lb：$4.75 | 大号标准 1~2lb：$6.73

### 工具B：8维度加权评分器
所有技能均使用。脚本路径：`scripts/scorer.py`

**使用方法：**
1. 根据数据分析结果填入各维度得分（0~10）
2. 设置 `seller` 变量（trade/factory/boutique）
3. 写入 `/tmp/score.py` 并执行 `python3 /tmp/score.py`

**8个维度：**
- market（市场吸引力）/ competition（竞争强度·反向）/ diff（差异化空间）/ traffic（流量获取·反向）
- supply（供应链优势）/ demand（用户需求强度）/ capital（资本效率）/ risk（风险系数·反向）

### 工具C：数据保存器
分析完成后将数据保存至本地 Excel，方便复盘与决策留档。脚本路径：`scripts/save_data.py`

**触发时机：**
- 用户明确要求保存/导出数据时
- full-evaluation 报告完成后主动询问：「是否将分析数据保存到本地 Excel？」

**使用方法：**
1. 分析完成后，将各模块采集到的数据填入脚本顶部变量
2. 修改 `TASK_NAME` 为分析对象名称（如「硅胶冰块托盘」）
3. 写入 `/tmp/save_data.py` 并执行 `python3 /tmp/save_data.py`
4. Excel 默认保存至桌面，文件名格式：`数据类型_YYYYMMDD_HHMMSS.xlsx`
