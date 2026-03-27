---
name: amazon-selection-v2
description: |
  Amazon 亚马逊选品分析技能包 v2.0，整合 Sorftime、卖家精灵、Jina、1688 四大数据源。
  包含 5 个专项技能，自动识别用户意图并路由到对应技能：
  · 市场侦察 (amazon-market-scout): 分析XX市场、XX类目好做吗、XX赛道值不值得进、评估XX品类
  · 竞品解剖 (amazon-product-spy): 分析ASIN、帮我研究这个竞品、解剖[产品名]、竞品分析
  · 蓝海发现 (amazon-niche-finder): 帮我找蓝海产品、推荐好做的品类、找机会点、找新品方向
  · 利润实验室 (amazon-profit-lab): 帮我算利润、核算成本、算一下ROI、利润分析、值不值得做
  · 综合评估 (amazon-full-evaluation): 全面评估XX、完整选品报告、综合分析、帮我做最终决策

  遇到任何亚马逊选品、产品分析、市场调研、利润核算相关请求时必须激活此技能。
---

# Amazon 选品分析技能包 v2.0
> Sorftime · 卖家精灵 · Jina · 1688 — 5技能 · SWOT · 生命周期 · 8维度评分

## 意图路由

收到用户请求后，先匹配技能，再读取对应 references/ 文件获取完整指令：

| 用户意图关键词 | 技能 | 读取文件 |
|---|---|---|
| 分析市场 / 品类好做吗 / 赛道 / 评估类目 | market-scout | `references/market-scout.md` |
| 分析ASIN / 竞品 / 解剖产品 / 这个产品怎么样 | product-spy | `references/product-spy.md` |
| 找蓝海 / 推荐品类 / 找机会 / 新品方向 | niche-finder | `references/niche-finder.md` |
| 算利润 / 核算成本 / ROI / 值不值得做 | profit-lab | `references/profit-lab.md` |
| 全面评估 / 完整报告 / 综合分析 / 最终决策 | full-evaluation | `references/full-evaluation.md` |

> 意图不明确时，询问用户："您是想分析市场整体情况、还是研究特定竞品、还是找新品机会？"

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
- `nodeId` — category_search 返回值
- `product_detail` — 售价 / 尺寸 / 重量 / 类目
- `category_report` — 月销量 / 均价 / 评论分布 / 新品占比
- `1688价格区间` — ali1688_similar_product 返回值
- `keyword_detail` — 搜索量 / CPC

### 数据降级规则
- Jina 不可用 → 标注"站外趋势暂不可用"，跳过，不中断流程
- 卖家精灵无数据 → 用 `keyword_detail` CPC 替代，注明"估算值"
- 1688 货源 < 3 家 → 标注"⚠️ 供应链风险：货源稀缺"
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
