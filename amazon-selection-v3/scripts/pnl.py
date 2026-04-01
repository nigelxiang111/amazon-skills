# P&L 三情景计算器 v3.0 — Amazon 选品技能包
# 支持两种调用方式:
#   1. JSON参数: python pnl.py '{"price":29.99,"cogs_cny":45,...}'
#   2. 交互式: python pnl.py  (手动填入变量)

import json
import sys

# ═══════════════════════════════════════
# 默认参数（交互式模式使用）
# ═══════════════════════════════════════
DEFAULTS = {
    "price":           0.0,   # 售价 ($)
    "cogs_cny":        0.0,   # 1688中位采购价 (¥)
    "weight_kg":       0.0,   # 产品重量 (kg)
    "fba_fee":         0.0,   # FBA费用 ($)
    "commission_rate": 0.15,  # 亚马逊佣金率（默认15%）
    "acos_base":       0.25,  # 类目平均ACoS
    "monthly_target":  200,   # 月目标销量（件）
    "exchange_rate":   7.2,   # 人民币兑美元汇率
}

# ═══════════════════════════════════════
# 三情景定义
# ═══════════════════════════════════════
SCENARIOS = [
    ("乐观", 0.9,  1.5,  0.70),
    ("基准", 1.0,  5.0,  1.00),
    ("悲观", 1.1, 10.0,  1.40),
]

def calculate(params: dict) -> dict:
    """执行P&L计算，返回结构化结果"""
    p = {**DEFAULTS, **params}

    price           = float(p["price"])
    cogs_cny        = float(p["cogs_cny"])
    weight_kg       = float(p["weight_kg"])
    fba_fee         = float(p["fba_fee"])
    commission_rate = float(p["commission_rate"])
    acos_base       = float(p["acos_base"])
    monthly_target  = int(p["monthly_target"])
    exchange_rate   = float(p["exchange_rate"])

    # 输入验证
    if price <= 0:
        return {"error": "售价必须大于0"}
    if cogs_cny < 0:
        return {"error": "采购价不能为负数"}

    results = {}
    base_net = base_cogs = base_ship = 0

    for name, cny_m, ship_r, acos_m in SCENARIOS:
        cogs = cogs_cny * cny_m * 1.1 / exchange_rate
        ship = weight_kg * ship_r
        comm = price * commission_rate
        ads  = price * acos_base * acos_m
        ret  = price * 0.02
        cost = cogs + ship + fba_fee + comm + ads + ret
        net  = price - cost
        mg   = net / price * 100 if price > 0 else 0
        roi  = net / (cogs + ship) * 100 if (cogs + ship) > 0 else 0

        results[name] = {
            "net_profit": round(net, 2),
            "margin_pct": round(mg, 1),
            "roi_pct":    round(roi, 1),
            "monthly_profit": round(net * monthly_target, 0),
        }

        if name == "基准":
            base_net  = net
            base_cogs = cogs
            base_ship = ship

    # 盈亏平衡分析
    fixed   = base_cogs + base_ship + fba_fee + price * commission_rate + price * 0.02
    be_acos = (price - fixed) / price * 100 if price > 0 else 0
    denom   = 1 - commission_rate - acos_base - 0.02
    be_price = (base_cogs + base_ship + fba_fee) / denom if denom > 0 else 0

    # 启动资金估算
    batch   = monthly_target * 3
    p_cost  = base_cogs * batch
    s_cost  = base_ship * batch
    ad_bgt  = price * acos_base * monthly_target * 3
    buffer  = (p_cost + s_cost + ad_bgt) * 0.15
    total   = p_cost + s_cost + ad_bgt + buffer
    payback = total / (base_net * monthly_target) if base_net > 0 else None

    return {
        "scenarios": results,
        "breakeven": {
            "max_acos_pct": round(be_acos, 1),
            "min_price":    round(be_price, 2),
        },
        "startup": {
            "total_usd":      round(total, 0),
            "purchase_usd":   round(p_cost, 0),
            "shipping_usd":   round(s_cost, 0),
            "ads_budget_usd": round(ad_bgt, 0),
            "buffer_usd":     round(buffer, 0),
            "payback_months": round(payback, 1) if payback else "亏损",
        }
    }


def print_report(data: dict, params: dict):
    """打印人类可读报告"""
    if "error" in data:
        print(f"❌ 错误: {data['error']}")
        return

    p = {**DEFAULTS, **params}
    print(f"\n{'':16} {'乐观':>10} {'基准':>10} {'悲观':>10}")
    print("─" * 48)

    for name in ["乐观", "基准", "悲观"]:
        s = data["scenarios"][name]
        print(f"净利润 [{name}]   ${s['net_profit']:>8.2f}   {s['margin_pct']:>6.1f}%   ROI{s['roi_pct']:>6.1f}%")

    base = data["scenarios"]["基准"]
    print(f"月净利 [基准]    ${base['monthly_profit']:>8.0f}  (目标{p['monthly_target']}件/月)")

    be = data["breakeven"]
    print(f"\n─── 盈亏平衡分析 ───")
    print(f"广告ACoS上限: {be['max_acos_pct']:.1f}%（超过则亏损）")
    print(f"保本最低售价: ${be['min_price']:.2f}")

    st = data["startup"]
    print(f"\n─── 启动资金估算 ───")
    print(f"总启动资金: ${st['total_usd']:,.0f}")
    print(f"  采购${st['purchase_usd']:,.0f} + 头程${st['shipping_usd']:,.0f} + 广告${st['ads_budget_usd']:,.0f} + 缓冲${st['buffer_usd']:,.0f}")
    print(f"预计回本: 第{st['payback_months']}个月")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # JSON模式
        try:
            params = json.loads(sys.argv[1])
        except json.JSONDecodeError as e:
            print(json.dumps({"error": f"JSON解析失败: {str(e)}"}))
            sys.exit(1)

        result = calculate(params)

        # 如果有--json标志，只输出JSON
        if "--json" in sys.argv:
            print(json.dumps(result, ensure_ascii=False))
        else:
            print_report(result, params)
            print("\n" + json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # 交互式模式（手动填入）
        print("交互式模式：请直接修改脚本中的DEFAULTS变量后重新运行")
        print("或使用: python pnl.py '{\"price\":29.99,\"cogs_cny\":45}'")
