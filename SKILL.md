# Amazon 选品分析技能包 v2.0
Sorftime · 卖家精灵 · Jina — 5技能 · SWOT · 生命周期 · 8维度评分

## 生命周期速查表
| 阶段 | 新品占比 | 均评论数 | 入场建议 |
|------|---------|---------|---------|
| 导入期 | >30% | <100 | ✅最佳时机 |
| 成长期 | >20% | 100~500 | ✅黄金窗口 |
| 成熟前期 | 10~20% | 300~800 | ⚡需差异化 |
| 成熟后期 | <10% | >800 | ❌谨慎 |
| 衰退期 | <5% | 停增长 | ❌不进入 |

## Session 缓存协议（所有技能强制遵守）
每次 MCP 调用前，**先检查当前对话中是否已有该数据**，有则直接复用，不重复调用：
- `nodeId` — category_search 返回值
- `product_detail` — 售价 / 尺寸 / 重量 / 类目
- `category_report` — 月销量 / 均价 / 评论分布 / 新品占比
- `1688价格区间` — ali1688_similar_product 返回值
- `keyword_detail` — 搜索量 / CPC

## 数据降级规则（所有技能通用）
- Jina 不可用 → 标注"站外趋势暂不可用"，跳过，不中断流程
- 卖家精灵无数据 → 用 `keyword_detail` CPC 替代，注明"估算值"
- 1688 货源 < 3 家 → 标注"⚠️ 供应链风险：货源稀缺"
- Python 不可用 → 按计算器注释中的公式手动计算，结果完全等价

---

## 共享计算工具

### 工具A：P&L 三情景计算器
用于 profit-lab 和 full-evaluation。将 API 真实数据填入变量后写入文件执行：
`python3 /tmp/pnl.py`

```python
# P&L 三情景计算器 — 仅用内置运算，无需任何第三方库
# 不可用时：净利润 = 售价 - COGS - 头程 - FBA - 亚马逊佣金 - 广告费 - 退货损耗(2%)

# ↓ 将 API / 用户提供的真实数据填入以下变量
price           = 0.0   # 售价 ($)
cogs_cny        = 0.0   # 1688中位采购价 (¥)
weight_kg       = 0.0   # 产品重量 (kg)
fba_fee         = 0.0   # FBA费用 ($)，参考：小号$3.22 / 中号$4.75 / 大号$6.73
commission_rate = 0.15  # 亚马逊佣金率（默认15%，电子类8%）
acos_base       = 0.25  # 类目平均ACoS（卖家精灵获取）
monthly_target  = 200   # 月目标销量（件）
exchange_rate   = 7.2   # 汇率（美元/人民币）

# 三情景：(名称, 1688采购系数, 头程$/kg, ACoS系数)
scenarios = [
    ("乐观", 0.9,  1.5,  0.70),   # 25%分位低价·海运·低ACoS
    ("基准", 1.0,  5.0,  1.00),   # 中位价·快船·均ACoS
    ("悲观", 1.1, 10.0,  1.40),   # 75%分位高价·空运·高ACoS
]

print(f"{'':16} {'乐观':>10} {'基准':>10} {'悲观':>10}")
print("─" * 48)
base_net = 0
for name, cny_m, ship_r, acos_m in scenarios:
    cogs = cogs_cny * cny_m * 1.1 / exchange_rate   # COGS：采购价×1.1(损耗税)÷汇率
    ship = weight_kg * ship_r                         # 头程运费
    comm = price * commission_rate                    # 亚马逊佣金
    ads  = price * acos_base * acos_m                # 广告费
    ret  = price * 0.02                               # 退货损耗2%
    cost = cogs + ship + fba_fee + comm + ads + ret
    net  = price - cost
    mg   = net / price * 100 if price > 0 else 0
    roi  = net / (cogs + ship) * 100 if (cogs + ship) > 0 else 0
    if name == "基准":
        base_net = net
        base_cogs, base_ship = cogs, ship
    print(f"净利润 [{name}]   ${net:>8.2f}   {mg:>6.1f}%   ROI{roi:>6.1f}%")
print(f"月净利 [基准]    ${base_net * monthly_target:>8.0f}  (目标{monthly_target}件/月)")

# 盈亏平衡分析（基准情景）
print("\n─── 盈亏平衡分析 ───")
fixed  = base_cogs + base_ship + fba_fee + price * commission_rate + price * 0.02
be_acos  = (price - fixed) / price * 100 if price > 0 else 0
be_price = (base_cogs + base_ship + fba_fee) / (1 - commission_rate - acos_base - 0.02)
print(f"广告ACoS上限: {be_acos:.1f}%（超过则亏损）")
print(f"保本最低售价: ${be_price:.2f}")

# 启动资金估算（基准情景）
print("\n─── 启动资金估算 ───")
batch   = monthly_target * 3           # 首批3个月库存
p_cost  = base_cogs * batch            # 采购总额
s_cost  = base_ship * batch            # 头程总额
ad_bgt  = price * acos_base * monthly_target * 3  # 广告预算3个月
buffer  = (p_cost + s_cost + ad_bgt) * 0.15       # 缓冲15%
total   = p_cost + s_cost + ad_bgt + buffer
payback = total / (base_net * monthly_target) if base_net > 0 else float('inf')
print(f"总启动资金: ${total:,.0f}")
print(f"  采购${p_cost:,.0f} + 头程${s_cost:,.0f} + 广告${ad_bgt:,.0f} + 缓冲${buffer:,.0f}")
print(f"预计回本: 第{payback:.1f}个月")
```

---

### 工具B：8维度加权评分器
所有技能均使用。将数据分析结果填入各维度得分（0~10）后执行：
`python3 /tmp/score.py`

```python
# 8维度评分器 — 仅用内置运算，无需任何第三方库
# 不可用时：综合分 = Σ(各维度得分 × 权重)，权重见下方

seller = "trade"  # 填入：trade（贸易型）/ factory（工厂型）/ boutique（精品型）

# ↓ 根据数据分析后填入各维度得分（0~10分）
scores = {
    "market"     : 0.0,  # 市场吸引力：月销量规模+增速趋势+旺季时长
    "competition": 0.0,  # 竞争强度（反向）：Top3垄断系数+均评论数
    "diff"       : 0.0,  # 差异化空间：差评密度+价格空白+新品占比
    "traffic"    : 0.0,  # 流量获取（反向）：核心词CPC+卖家精灵竞争度
    "supply"     : 0.0,  # 供应链优势：1688货源丰富度+采购成本占比
    "demand"     : 0.0,  # 用户需求强度：搜索量+趋势+TikTok热度
    "capital"    : 0.0,  # 资本效率：毛利率+ROI+资金周转速度
    "risk"       : 0.0,  # 风险系数（反向）：自营占比+专利风险+合规复杂度
}

# 权重配置（各列合计100%）
W = {
    "trade"  : {"market":.15,"competition":.20,"diff":.15,"traffic":.15,
                "supply":.10,"demand":.10,"capital":.10,"risk":.05},
    "factory": {"market":.13,"competition":.18,"diff":.10,"traffic":.13,
                "supply":.20,"demand":.09,"capital":.15,"risk":.02},
    "boutique":{"market":.12,"competition":.18,"diff":.25,"traffic":.13,
                "supply":.05,"demand":.15,"capital":.08,"risk":.04},
}
w = W.get(seller, W["trade"])

labels = {"market":"市场吸引力","competition":"竞争强度  ","diff":"差异化空间",
          "traffic":"流量获取  ","supply":"供应链优势","demand":"用户需求  ",
          "capital":"资本效率  ","risk":"风险系数  "}

total = sum(scores[k] * w[k] for k in scores)
for k, lb in labels.items():
    bar = "█" * round(scores[k]) + "░" * (10 - round(scores[k]))
    print(f"  {lb} {bar} {scores[k]:.1f}  ({w[k]*100:.0f}%)")
print(f"  {'─'*38}")
print(f"  综合评分：{total:.1f} / 10")
verdict = "✅ 强烈推荐进入" if total>=7.5 else "⚡ 谨慎进入，需差异化" if total>=5 else "❌ 当前不建议进入"
print(f"  {verdict}")
```

---

# SKILL: amazon-market-scout

## Description
亚马逊市场赛道侦察技能。评估指定品类或赛道是否值得进入，输出生命周期定位、SWOT、8维度评分和入场建议。

**触发关键词**：分析XX市场、XX类目好做吗、XX赛道值不值得进、评估XX品类、XX市场怎么样、帮我看看XX

## Instructions

### 前置
若用户指定分析视角（供应链/资本效率/风险/时机/差异化/流量），后续重点深化该视角；未指定则全视角各输出1~2句。

### 第一阶段：快速筛选（满足任一则终止）
`mcp__sorftime__category_search_from_product_name` → 检查前3个类目：
- 所有类目月销量 < 500 → 终止："市场体量过小"
- 所有类目 Top3垄断 > 70% → 终止："竞争过于集中"
- 亚马逊自营占比 > 50% → 终止："自营主导，第三方空间极小"

通过后取**月销量最高且垄断系数最低的 TOP 2 类目**继续。

### 第二阶段：深度数据采集
【缓存检查】已有数据则跳过对应调用。

`mcp__sorftime__category_report` — 月销量/均价/评论分布/新品占比/旺季

【以下4个调用可并行执行】
- `mcp__sorftime__category_trend(SalesCount)`
- `mcp__sorftime__category_trend(NewProductSalesAmountShare)`
- `mcp__sorftime__category_trend(AmazonSalesAmountShare)`
- `mcp__sorftime__category_trend(Top3ProductSalesAmountShare)`

【以下2个调用可并行执行】
- `mcp__sorftime__category_keywords` → 获取核心词列表
- `mcp__sorftime__keyword_detail`（TOP3核心词）→ 搜索量/CPC

卖家精灵 — 验证关键词精确搜索量和竞争度评分（与Sorftime数据交叉验证，取均值）

### 第三阶段：框架分析
1. **生命周期定位** — 对照速查表，综合SalesCount趋势 + 新品占比 + 均评论数 + 核心词趋势
2. **市场层SWOT**
   - S：月销量规模 / 增速 / 新品机会占比 / 价格带均衡性
   - W：Top3垄断系数 / 评论数壁垒 / 亚马逊自营威胁
   - O：价格带空白 / 新兴关键词 / 细分人群未满足需求
   - T：亚马逊自营扩张 / 头部品牌护城河 / 合规收紧
3. **评分** — 用**共享工具B**（8维度评分器）计算综合分

### 第四阶段：输出
```
📊 市场侦察报告：[类目]（[站点]）
📅 生命周期：[阶段] | ⏰ 入场时机：[最佳/良好/一般/不推荐]
📈 月销：X件 | 均价：$X | Top3垄断：X% | 自营：X% | 新品占比：X%
🔑 核心词：[词1]X万/月 $X.XX | [词2]... | [词3]...
🔲 SWOT：✅[优势2~3条] ⚠️[劣势] 🚀[机会] ⛔[威胁]
📐 8维度评分（工具B输出）综合：X.X/10
🎯 [✅推荐/⚡谨慎/❌不建议] · 核心理由 · 推荐切入方向 · 重点关键词
```

---

# SKILL: amazon-product-spy

## Description
亚马逊竞品深度解剖技能。从流量结构、用户口碑、成本利润、生命周期四维度全面剖析竞品，定位可超越的差异化机会点。

**触发关键词**：分析ASIN、帮我研究这个竞品、解剖[产品名]、[ASIN]的情况、这个产品怎么样、竞品分析

## Instructions

### 前置：ASIN提取
- 用户提供链接 → 提取B开头10位字符
- 用户提供产品名 → `mcp__sorftime__product_search` 取月销量最高结果
- 用户直接提供ASIN → 直接使用

### 第一阶段：快速核查
【缓存检查】product_detail 已有则跳过。
`mcp__sorftime__product_detail` → 月销量 < 50件则询问用户是否继续。

### 第二阶段：深度采集
【缓存检查】先检查对话中已有数据。

`mcp__sorftime__product_report` — 月销量/销额/BSR/价格/评分/评论数

【以下5个调用可并行执行】
- `mcp__sorftime__product_trend(SalesVolume)`
- `mcp__sorftime__product_trend(Price)`
- `mcp__sorftime__product_trend(Rank)`
- `mcp__sorftime__product_reviews(Negative)`
- `mcp__sorftime__product_reviews(Positive)`

卖家精灵 ASIN反查 — **最重要步骤，优先执行**：精确搜索量/广告词/自然排名/流量来源占比
`mcp__sorftime__product_traffic_terms` — 取前50条流量词（关注近30天曝光词）
`mcp__sorftime__ali1688_similar_product` — 采购价（取25%~75%分位）

### 第三阶段：框架分析
1. **生命周期** — SalesVolume趋势 + Price趋势 + Rank趋势综合判断
2. **流量结构拆解** — 自然搜索词 / 广告词 / 长尾词 三类分类
3. **竞品层SWOT**
   - S：高评分/多评论/强排名/品牌认知/变体丰富
   - W：差评集中的功能缺失/变体不足/包装差/客服慢
   - O：差评改进空间/未覆盖关键词/价格带断层
   - T：专利侵权可能/品牌强保护/大卖家跟进
4. **用户痛点提炼**（来自差评）— 功能性/情感性/感知性/隐性需求分类
5. **成本估算** — COGS=1688中位价×1.1÷7.2；FBA查尺寸档；佣金=售价×15%
6. **评分** — 用**共享工具B**（8维度评分器），重点强化差异化空间维度

### 第四阶段：输出
```
🔍 竞品解剖：[产品名] ASIN:[X]
📅 生命周期：[阶段] | 研究价值：[高/中/低]
📊 月销X件 | $X | BSR#X | ⭐X.X (X评论) | 主力变体：[描述]
🔑 流量词TOP10：[词] X万/月 | 自然第X位 / 广告词
🔲 竞品SWOT（重点标注W弱点=你的机会）
😤 用户痛点TOP3（频率+原文摘录）
👍 好评亮点（值得保留的设计点）
💰 净利润$X | 毛利率X% | ROI X%
📐 8维度评分（工具B输出）综合：X.X/10
🎯 差异化机会：[具体改进方向] · 建议售价$X~$X · 优先主攻关键词
```

---

# SKILL: amazon-niche-finder

## Description
亚马逊蓝海机会发现技能。主动发现低竞争、高需求、处于导入期或成长期的细分类目，输出TOP3蓝海机会。

**触发关键词**：帮我找蓝海产品、推荐一个好做的品类、找机会点、有没有好做的市场、找一个新品方向、主动发现机会

## Instructions

### 前置：收集用户偏好（缺失则询问）
大品类方向（家居/电子/宠物/户外/厨房/不限）| 价格带 | 目标站点（默认US）| 卖家类型

### 第一阶段：类目筛选
- 用户指定品类 → `mcp__sorftime__category_tree` 获取topNodeId → `category_search_from_top_node`
- 未指定品类 → `mcp__sorftime__search_categories_broadly`

必须同时满足的筛选参数：
```
month_sales_volume_min:     1000
top3Product_sales_share_max: 0.40
amazonOwned_sales_share_max: 0.10
ratings_count_max:            500
newproduct_sales_share_min:  0.15
```
结果不足8个时放宽 `ratings_count_max` 至 800 重新搜索。
按价格偏好追加 price_min/price_max。取月销量最高的前8个候选。

### 第二阶段：生命周期验证（淘汰不合格）
对前8个候选调用：
- `mcp__sorftime__category_trend(SalesCount)` — 验证近6个月趋势
- `mcp__sorftime__category_trend(NewProductSalesAmountShare)` — 验证新品活跃度

淘汰条件（满足任一）：销量连续3个月下降 | 新品占比 < 10%

保留通过验证的 TOP3~5 进入深度验证。

### 第三阶段：深度验证（对保留类目并行执行）
【以下调用可并行执行】
- `mcp__sorftime__category_keywords` + 卖家精灵验证搜索量（<1000/月标注"细分过窄"）
- `mcp__sorftime__tiktok_similar_product` — TikTok销量验证（用英文产品名效果更好）
- Jina `mcp__jina-mcp-server__search_web` — 搜索"[产品英文名] trending 2025 2026"
- `mcp__sorftime__ali1688_similar_product` — 采购成本必须 < 售价25%，否则标注风险
- `mcp__sorftime__potential_product` — 潜力单品参考样本

### 第四阶段：蓝海SWOT + 输出
对TOP3建立蓝海层SWOT：
- S：低竞争/供应链成熟/搜索量上升/TikTok已有热度
- W：市场体量有限/消费者认知度低/单价偏低
- O：先发优势/关键词排名抢占/品牌建设窗口
- T：大卖家快速跟进/市场过快成熟/价格战提前

```
🌊 蓝海机会报告 | [品类] | $X~$X | [站点]
共发现X个蓝海机会，推荐TOP3：

🥇 机会一：[类目名称]
  📅 [成长期↗] 窗口约X个月
  市场：X万件/月 | 均价$X | Top3垄断X% | 新品X%
  🔑 核心词：[词]X万/月↑  📱TikTok热度：[高/中/低]
  🏭 供应链：1688货丰富，采购约¥X~¥X（占售价X%）
  🔲 SWOT + 🎯 切入建议：差异化方向/建议售价/首批备货量/优先关键词

🥈 机会二：...（同上格式）
🥉 机会三：...（同上格式）

📋 综合推荐：最优选[X] | 资金有限选[X] | 求快变现选[X]
```

---

# SKILL: amazon-profit-lab

## Description
亚马逊利润实验室技能。核算产品利润可行性，输出三情景P&L表、盈亏平衡分析、资本效率报告和利润层SWOT。

**触发关键词**：帮我算利润、核算成本、这个品能不能做、算一下ROI、利润分析、成本核算、值不值得做（财务角度）

## Instructions

### 前置：确认信息（缺失则询问）
- 产品 ASIN 或售价
- 产品尺寸/重量（计算FBA费和头程运费必须）
- 目标站点（默认US）
- 月目标销量（默认200件）

### 第一阶段：数据采集
【缓存检查】以下数据若已在对话中存在则跳过调用。

【以下调用可并行执行】
- `mcp__sorftime__product_detail`（有ASIN时）— 售价/类目/尺寸重量
- `mcp__sorftime__ali1688_similar_product` — 采购价（取第1页，排除最高/最低，取25%~75%分位）
- `mcp__sorftime__keyword_detail`（核心词）— CPC 参考
- 卖家精灵 — 类目平均 ACoS

FBA费用参考（无法获取时按此估算）：
- 小号标准≤4oz：$3.22 | 中号标准≤1lb：$4.75 | 大号标准1~2lb：$6.73

### 第二阶段：P&L计算
使用**共享工具A（P&L三情景计算器）**：
1. 将上一阶段数据填入计算器变量（price / cogs_cny / weight_kg / fba_fee / commission_rate / acos_base / monthly_target）
2. 将脚本写入 `/tmp/pnl.py` 并运行 `python3 /tmp/pnl.py`
3. 将输出结果纳入报告

**Python 不可用时**：按计算器注释中的公式逐项手算，结果完全等价。

### 第三阶段：利润层SWOT + 评分
- S：毛利率>25% / ROI>50% / 供应链货源稳定 / 资金周转快
- W：广告依赖高(ACoS>30%) / 库存资金压力 / 头程成本占比高
- O：1688降价谈判空间 / 差异化提价5~15% / 转化率提升降ACoS
- T：FBA费用年度上涨 / 汇率波动 / 原材料涨价

使用**共享工具B（8维度评分器）**，重点强化资本效率维度（权重↑）。

### 第四阶段：输出
```
💰 利润实验室：[产品/ASIN]（[站点]）
📊 三情景P&L（来自工具A输出）
⚖️ 盈亏平衡：ACoS上限X% | 保本售价$X
💼 总启动资金$X,XXX | 月净利$XXX | 回本第X月
📐 8维度评分（工具B输出）综合：X.X/10
🔲 利润层SWOT
🎯 可行性判断：[✅利润可行/⚡边际产品需优化/❌当前不可行]
   核心问题 + 最关键优化动作（供应链降本/定价调整/ACoS优化目标）
```

---

# SKILL: amazon-full-evaluation

## Description
亚马逊选品综合评估技能。整合市场、竞品、机会、利润四大模块全量数据，生成最终投资决策报告。

**触发关键词**：全面评估XX、给我一份完整选品报告、综合分析XX、帮我做最终决策、XX到底做不做、我要一份完整的XX分析

## Instructions

### 前置：明确参数
评估对象（ASIN或类目名）| 站点（默认US）| 卖家类型（工厂/精品/贸易，默认贸易）| 预算规模（小<$5K / 中$5K~$30K / 大>$30K）

### 第一阶段：全量数据采集
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
- 卖家精灵 ASIN反查 — **最高优先级，优先执行**

**模块C：机会层**
- 【并行】`mcp__sorftime__tiktok_similar_product`
- 【并行】Jina `mcp__jina-mcp-server__search_web` — "[产品名] patent amazon" + "[产品名] trending 2026"

**模块D：利润层**
- 【缓存检查】1688价格若已有则复用
- 【并行】`mcp__sorftime__ali1688_similar_product` + 卖家精灵（类目ACoS + CPC）

### 第二阶段：生命周期综合定位
- 有ASIN → 以 `product_trend(SalesVolume)` 为主，category_trend 辅助
- 无ASIN → 以 `category_trend(SalesCount + NewProductSalesAmountShare)` 为主
- 数据冲突时 → 说明差异来源，给综合判断

输出：[生命周期阶段] + 入场时机评级 [S/A/B/C/D] + 窗口期约X个月

### 第三阶段：P&L三情景计算
使用**共享工具A（P&L三情景计算器）**：
将模块D数据（1688价格/卖家精灵ACoS/产品detail中的重量售价）填入计算器变量，写入 `/tmp/pnl.py` 执行。
Python 不可用时按注释公式手算。

### 第四阶段：8维度评分
使用**共享工具B（8维度评分器）**：
将 `seller` 变量设为用户卖家类型，根据全量数据分析为每个维度打分（0~10），写入 `/tmp/score.py` 执行。
Python 不可用时加权手算：综合分 = Σ(各维度分 × 权重)。

### 第五阶段：综合SWOT（整合四模块，每象限≤5条）
- **S（核心优势）**：跨模块最具说服力（市场大+成本低+需求强）
- **W（致命劣势）**：最可能导致失败，按严重度排序，≤3条
- **O（即时机会）**：最值得立即行动，具体可操作
- **T（首要威胁）**：必须提前防范，具体化

### 第六阶段：7视角个性化建议（每条1~2句精准建议）
🏭 供应链：最大成本压缩机会在哪里
🧠 用户心理：最核心的1个未满足需求（来自差评）
💰 资本效率：基于[预算规模]建议首批库存量和启动节奏
🛡️ 风险防御：最需规避的1个风险 + 具体规避动作
⏰ 市场时机：窗口期剩余时间 + 建议决策截止时间
✨ 差异化：最可行的1个方向（SWOT机会象限+差评双重验证）
🔑 流量：最容易突破的1~2个关键词（竞争度最低+搜索量合理）

### 第七阶段：最终决策输出
```
🏆 综合评估报告：[产品/类目] | [站点] | [卖家类型] | 预算[规模]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 生命周期：[阶段] | 入场时机：[S/A/B/C/D] | 窗口期约X个月
📐 8维度评分（工具B输出）
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

若预算"小"（<$5K）：特别对比总启动资金 vs 用户预算缺口，给出分阶段切入建议。
卖家精灵专利粗筛：搜索"[产品名] patent amazon"，出现专利结果则在风险系数维度扣分并标注。
