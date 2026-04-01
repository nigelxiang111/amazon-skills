# 8维度加权评分器 v3.0 — Amazon 选品技能包
# 支持两种调用方式:
#   1. JSON参数: python scorer.py '{"seller":"trade","scores":{...}}'
#   2. 交互式: python scorer.py  (手动填入变量)

import json
import sys

# ═══════════════════════════════════════
# 权重配置
# ═══════════════════════════════════════
WEIGHTS = {
    "trade"   : {"market": .15, "competition": .20, "diff": .15, "traffic": .15,
                 "supply": .10, "demand": .10, "capital": .10, "risk": .05},
    "factory" : {"market": .13, "competition": .18, "diff": .10, "traffic": .13,
                 "supply": .20, "demand": .09, "capital": .15, "risk": .02},
    "boutique": {"market": .12, "competition": .18, "diff": .25, "traffic": .13,
                 "supply": .05, "demand": .15, "capital": .08, "risk": .04},
}

LABELS = {
    "market"     : "市场吸引力",
    "competition": "竞争强度  ",
    "diff"       : "差异化空间",
    "traffic"    : "流量获取  ",
    "supply"     : "供应链优势",
    "demand"     : "用户需求  ",
    "capital"    : "资本效率  ",
    "risk"       : "风险系数  ",
}

REVERSE_DIMS = {"competition", "traffic", "risk"}  # 反向维度：分越低说明该项越差


def calculate(params: dict) -> dict:
    """执行评分计算，返回结构化结果"""
    seller = params.get("seller", "trade")
    scores = params.get("scores", {})

    # 验证卖家类型
    if seller not in WEIGHTS:
        return {"error": f"不支持的卖家类型: {seller}，支持: {', '.join(WEIGHTS.keys())}"}

    # 验证分数范围
    for dim, score in scores.items():
        if not (0 <= float(score) <= 10):
            return {"error": f"维度 {dim} 分数超出范围: {score}，应在0-10之间"}

    w = WEIGHTS[seller]
    total = sum(float(scores.get(k, 0)) * w[k] for k in w)

    if total >= 7.5:
        verdict = "✅ 强烈推荐进入"
        verdict_en = "STRONG_BUY"
    elif total >= 5.0:
        verdict = "⚡ 谨慎进入，需差异化策略"
        verdict_en = "CAUTIOUS"
    else:
        verdict = "❌ 当前不建议进入"
        verdict_en = "AVOID"

    breakdown = {}
    for k in w:
        score = float(scores.get(k, 0))
        breakdown[k] = {
            "label":       LABELS[k].strip(),
            "score":       score,
            "weight_pct":  round(w[k] * 100, 0),
            "weighted":    round(score * w[k], 3),
            "is_reverse":  k in REVERSE_DIMS,
        }

    return {
        "seller_type": seller,
        "total_score": round(total, 2),
        "verdict":     verdict,
        "verdict_code": verdict_en,
        "breakdown":   breakdown,
    }


def print_report(data: dict):
    """打印人类可读报告"""
    if "error" in data:
        print(f"❌ 错误: {data['error']}")
        return

    print(f"\n卖家类型：{data['seller_type']}  （贸易型=trade / 工厂型=factory / 精品型=boutique）\n")

    for k, info in data["breakdown"].items():
        bar  = "█" * round(info["score"]) + "░" * (10 - round(info["score"]))
        flag = "↓好" if info["is_reverse"] else ""
        print(f"  {info['label']} {bar} {info['score']:.1f}  ({info['weight_pct']:.0f}%){flag}")

    print(f"  {'─' * 42}")
    print(f"  综合评分：{data['total_score']:.1f} / 10\n")
    print(f"  {data['verdict']}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            params = json.loads(sys.argv[1])
        except json.JSONDecodeError as e:
            print(json.dumps({"error": f"JSON解析失败: {str(e)}"}))
            sys.exit(1)

        result = calculate(params)

        if "--json" in sys.argv:
            print(json.dumps(result, ensure_ascii=False))
        else:
            print_report(result)
            print("\n" + json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("使用方式: python scorer.py '{\"seller\":\"trade\",\"scores\":{\"market\":7,\"competition\":6,...}}'")
        print("卖家类型: trade（贸易型）/ factory（工厂型）/ boutique（精品型）")
