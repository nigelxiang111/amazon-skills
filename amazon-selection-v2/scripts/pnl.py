# P&L 三情景计算器 v2.0 — Amazon 选品技能包
# 仅用 Python 内置运算，无需任何第三方库
# 不可用时：净利润 = 售价 - COGS - 头程 - FBA - 亚马逊佣金 - 广告费 - 退货损耗(2%)
#
# 使用方法：将 API / 用户提供的真实数据填入以下变量，然后执行此脚本

# ═══════════════════════════════════════
# ↓ 填入真实数据（必填项）
# ═══════════════════════════════════════
price           = 0.0   # 售价 ($)
cogs_cny        = 0.0   # 1688中位采购价 (¥)，取25%~75%分位均值
weight_kg       = 0.0   # 产品重量 (kg)
fba_fee         = 0.0   # FBA费用 ($)  参考: 小号$3.22 / 中号$4.75 / 大号$6.73
commission_rate = 0.15  # 亚马逊佣金率（默认15%，电子类8%，书籍类15%）
acos_base       = 0.25  # 类目平均ACoS（从卖家精灵获取；无数据时用0.25）
monthly_target  = 200   # 月目标销量（件）
exchange_rate   = 7.2   # 人民币兑美元汇率

# ═══════════════════════════════════════
# 三情景定义：(名称, 1688采购系数, 头程$/kg, ACoS系数)
# ═══════════════════════════════════════
scenarios = [
    ("乐观", 0.9,  1.5,  0.70),   # 25%分位低价 · 海运 · 低ACoS
    ("基准", 1.0,  5.0,  1.00),   # 中位价 · 快船 · 均ACoS
    ("悲观", 1.1, 10.0,  1.40),   # 75%分位高价 · 空运 · 高ACoS
]

# ═══════════════════════════════════════
# 计算与输出
# ═══════════════════════════════════════
print(f"\n{'':16} {'乐观':>10} {'基准':>10} {'悲观':>10}")
print("─" * 48)

base_net = 0
base_cogs = 0
base_ship = 0

for name, cny_m, ship_r, acos_m in scenarios:
    cogs = cogs_cny * cny_m * 1.1 / exchange_rate   # COGS：采购价×系数×1.1(税损)÷汇率
    ship = weight_kg * ship_r                         # 头程运费
    comm = price * commission_rate                    # 亚马逊佣金
    ads  = price * acos_base * acos_m                # 广告费
    ret  = price * 0.02                               # 退货损耗2%
    cost = cogs + ship + fba_fee + comm + ads + ret
    net  = price - cost
    mg   = net / price * 100 if price > 0 else 0
    roi  = net / (cogs + ship) * 100 if (cogs + ship) > 0 else 0

    if name == "基准":
        base_net  = net
        base_cogs = cogs
        base_ship = ship

    print(f"净利润 [{name}]   ${net:>8.2f}   {mg:>6.1f}%   ROI{roi:>6.1f}%")

print(f"月净利 [基准]    ${base_net * monthly_target:>8.0f}  (目标{monthly_target}件/月)")

# ── 盈亏平衡分析（基准情景）──────────────────────
print("\n─── 盈亏平衡分析 ───")
fixed   = base_cogs + base_ship + fba_fee + price * commission_rate + price * 0.02
be_acos = (price - fixed) / price * 100 if price > 0 else 0
be_price = (base_cogs + base_ship + fba_fee) / (1 - commission_rate - acos_base - 0.02) if (1 - commission_rate - acos_base - 0.02) > 0 else 0
print(f"广告ACoS上限: {be_acos:.1f}%（超过则亏损）")
print(f"保本最低售价: ${be_price:.2f}")

# ── 启动资金估算（基准情景）──────────────────────
print("\n─── 启动资金估算 ───")
batch   = monthly_target * 3                            # 首批3个月库存
p_cost  = base_cogs * batch                             # 采购总额
s_cost  = base_ship * batch                             # 头程总额
ad_bgt  = price * acos_base * monthly_target * 3        # 广告预算3个月
buffer  = (p_cost + s_cost + ad_bgt) * 0.15             # 缓冲15%
total   = p_cost + s_cost + ad_bgt + buffer
payback = total / (base_net * monthly_target) if base_net > 0 else float('inf')

print(f"总启动资金: ${total:,.0f}")
print(f"  采购${p_cost:,.0f} + 头程${s_cost:,.0f} + 广告${ad_bgt:,.0f} + 缓冲${buffer:,.0f}")
print(f"预计回本: 第{payback:.1f}个月")
