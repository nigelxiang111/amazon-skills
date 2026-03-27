# 8维度加权评分器 v2.0 — Amazon 选品技能包
# 仅用 Python 内置运算，无需任何第三方库
# 不可用时：综合分 = Σ(各维度得分 × 权重)，权重见下方
#
# 使用方法：根据数据分析结果填入各维度得分，设置卖家类型，然后执行此脚本

# ═══════════════════════════════════════
# ↓ 设置卖家类型
# ═══════════════════════════════════════
seller = "trade"   # 填入: trade（贸易型） / factory（工厂型） / boutique（精品型）

# ═══════════════════════════════════════
# ↓ 根据数据分析填入各维度得分（0~10分）
# ═══════════════════════════════════════
scores = {
    "market"     : 0.0,  # 市场吸引力：月销量规模 + 增速趋势 + 旺季时长
    "competition": 0.0,  # 竞争强度（反向，分低=竞争弱=好）：Top3垄断系数 + 均评论数
    "diff"       : 0.0,  # 差异化空间：差评密度 + 价格空白 + 新品占比
    "traffic"    : 0.0,  # 流量获取（反向，分低=流量贵=不好）：核心词CPC + 竞争度
    "supply"     : 0.0,  # 供应链优势：1688货源丰富度 + 采购成本占比
    "demand"     : 0.0,  # 用户需求强度：搜索量 + 趋势 + TikTok热度
    "capital"    : 0.0,  # 资本效率：毛利率 + ROI + 资金周转速度
    "risk"       : 0.0,  # 风险系数（反向，分低=风险高=不好）：自营占比 + 专利 + 合规
}

# ═══════════════════════════════════════
# 权重配置（各列合计100%）
# ═══════════════════════════════════════
W = {
    "trade"   : {"market": .15, "competition": .20, "diff": .15, "traffic": .15,
                 "supply": .10, "demand": .10, "capital": .10, "risk": .05},
    "factory" : {"market": .13, "competition": .18, "diff": .10, "traffic": .13,
                 "supply": .20, "demand": .09, "capital": .15, "risk": .02},
    "boutique": {"market": .12, "competition": .18, "diff": .25, "traffic": .13,
                 "supply": .05, "demand": .15, "capital": .08, "risk": .04},
}
w = W.get(seller, W["trade"])

# ═══════════════════════════════════════
# 计算与输出
# ═══════════════════════════════════════
labels = {
    "market"     : "市场吸引力",
    "competition": "竞争强度  ",
    "diff"       : "差异化空间",
    "traffic"    : "流量获取  ",
    "supply"     : "供应链优势",
    "demand"     : "用户需求  ",
    "capital"    : "资本效率  ",
    "risk"       : "风险系数  ",
}

reverse_dims = {"competition", "traffic", "risk"}  # 反向维度：分越低说明该项越差

print(f"\n卖家类型：{seller}  （贸易型=trade / 工厂型=factory / 精品型=boutique）\n")
total = sum(scores[k] * w[k] for k in scores)

for k, lb in labels.items():
    bar = "█" * round(scores[k]) + "░" * (10 - round(scores[k]))
    flag = "↓好" if k in reverse_dims else ""
    print(f"  {lb} {bar} {scores[k]:.1f}  ({w[k]*100:.0f}%){flag}")

print(f"  {'─' * 42}")
print(f"  综合评分：{total:.1f} / 10\n")

if total >= 7.5:
    verdict = "✅ 强烈推荐进入"
elif total >= 5.0:
    verdict = "⚡ 谨慎进入，需差异化策略"
else:
    verdict = "❌ 当前不建议进入"

print(f"  {verdict}")
