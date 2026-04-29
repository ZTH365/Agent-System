from utils.llm import call_llm_json


# ========================
# 规则增强
# ========================
HIGH_RISK_KEYWORDS = [
    "auth", "permission", "payment", "transaction",
    "delete", "drop", "migration", "rollback"
]


def detect_high_risk_patterns(diff: str):
    """简单规则检测（辅助 LLM）"""
    hits = []
    lower_diff = diff.lower()

    for kw in HIGH_RISK_KEYWORDS:
        if kw in lower_diff:
            hits.append(kw)

    return hits


# ========================
# 主风险分析函数
# ========================
def analyze_risk(diff: str) -> dict:
    """
    返回结构化风险分析结果
    """

    # 规则层（先验信号）
    rule_hits = detect_high_risk_patterns(diff)

    prompt = f"""
你是资深后端架构师，请对代码变更进行风险评估。

代码变更：
{diff[:6000]}

规则检测到的潜在高风险关键词：
{rule_hits}

请严格返回 JSON：
{{
  "risk_level": "low | medium | high",
  "risk_score": 0-100,
  "summary": "总体风险总结",
  "issues": [
    {{
      "type": "风险类型",
      "description": "问题描述",
      "impact": "影响范围"
    }}
  ],
  "affected_modules": ["模块1", "模块2"],
  "recommendations": ["建议1", "建议2"]
}}
"""

    result = call_llm_json(prompt)

    # ========================
    # 后处理 增强稳定性
    # ========================
    if not isinstance(result, dict):
        return {
            "risk_level": "unknown",
            "risk_score": 50,
            "summary": "LLM output invalid",
            "issues": [],
            "affected_modules": [],
            "recommendations": [],
            "rule_hits": rule_hits
        }

    # 补充规则信号（用于 reviewer 或后续决策）
    result["rule_hits"] = rule_hits

    # 简单校正逻辑（工程感）
    if rule_hits and result.get("risk_level") == "low":
        result["risk_level"] = "medium"
        result["summary"] += "（规则检测到潜在高风险关键词，已上调风险等级）"

    return result
