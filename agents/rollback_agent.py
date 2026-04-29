from utils.llm import call_llm_json


# ========================
# 规则增强 识别高风险变更
# ========================
CRITICAL_KEYWORDS = [
    "migration", "schema", "delete", "update", "transaction",
    "payment", "order", "inventory"
]


def detect_critical_changes(diff: str):
    hits = []
    lower_diff = diff.lower()

    for kw in CRITICAL_KEYWORDS:
        if kw in lower_diff:
            hits.append(kw)

    return hits


# ========================
# 主函数
# ========================
def suggest_rollback(diff: str) -> dict:
    """
    生成结构化回滚方案
    """

    critical_hits = detect_critical_changes(diff)

    prompt = f"""
你是资深后端架构师，请为以下代码变更设计回滚方案。

代码变更：
{diff[:6000]}

检测到的关键风险关键词：
{critical_hits}

请严格返回 JSON：
{{
  "rollback_needed": true/false,
  "confidence": 0-100,
  "summary": "总体判断",
  "triggers": [
    "触发回滚的条件，例如错误率 > 5%"
  ],
  "rollback_steps": [
    "步骤1",
    "步骤2"
  ],
  "data_risks": [
    {{
      "type": "数据风险类型",
      "description": "风险说明",
      "mitigation": "缓解措施"
    }}
  ],
  "fallback_strategy": "降级或兜底方案"
}}
"""

    result = call_llm_json(prompt)

    # ========================
    # 后处理 增强稳定性 
    # ========================
    if not isinstance(result, dict):
        return {
            "rollback_needed": True,
            "confidence": 50,
            "summary": "LLM 输出异常，建议保守处理",
            "triggers": ["unknown"],
            "rollback_steps": ["git revert 当前变更"],
            "data_risks": [],
            "fallback_strategy": "启用只读模式",
            "critical_hits": critical_hits
        }

    # 注入规则信号
    result["critical_hits"] = critical_hits

    # 简单校正逻辑（工程加分）
    if critical_hits and not result.get("rollback_needed"):
        result["rollback_needed"] = True
        result["summary"] += "（检测到关键变更，已强制建议准备回滚方案）"

    return result
