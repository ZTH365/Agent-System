import json
import time
from concurrent.futures import ThreadPoolExecutor

from utils.git_utils import get_git_diff
from agents.risk_agent import analyze_risk
from agents.test_agent import generate_tests
from agents.rollback_agent import suggest_rollback
from utils.llm import call_llm


def plan(diff):
    prompt = f"""
你是系统调度 Agent，请根据代码变更规模决定执行策略：

{diff[:2000]}

输出 JSON：
{{
  "run_risk": true/false,
  "run_test": true/false,
  "run_rollback": true/false,
  "reason": ""
}}
"""
    result = call_llm(prompt)

    try:
        return json.loads(result)
    except:
        # fallback：默认全执行
        return {
            "run_risk": True,
            "run_test": True,
            "run_rollback": True,
            "reason": "fallback"
        }


def review(all_outputs):
    prompt = f"""
你是 Reviewer Agent，请评估以下分析结果的质量：

{json.dumps(all_outputs, ensure_ascii=False, indent=2)}

输出：
1. 是否存在明显问题
2. 哪些结论不可靠
3. 总体置信度（0-100）
"""
    return call_llm(prompt)


def run_pipeline():
    print("🚀 Starting Enhanced Agent System...\n")

    start_time = time.time()

    diff = get_git_diff()
    if not diff.strip():
        print("❌ No code changes detected")
        return

    print("📦 Code change detected\n")

    # Step 1: Planner 决策
    plan_result = plan(diff)
    print("🧠 Plan সিদ্ধান্ত:")
    print(plan_result)
    print()

    results = {}

    # Step 2: 并发执行 Agents
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {}

        if plan_result.get("run_risk"):
            futures["risk"] = executor.submit(analyze_risk, diff)

        if plan_result.get("run_test"):
            futures["test"] = executor.submit(generate_tests, diff)

        if plan_result.get("run_rollback"):
            futures["rollback"] = executor.submit(suggest_rollback, diff)

        for name, future in futures.items():
            try:
                results[name] = future.result(timeout=60)
            except Exception as e:
                results[name] = f"Error: {str(e)}"

    # Step 3: Reviewer 二次校验
    review_result = review(results)

    # Step 4: 汇总输出（结构化）
    final_output = {
        "plan": plan_result,
        "analysis": results,
        "review": review_result,
        "meta": {
            "execution_time": round(time.time() - start_time, 2)
        }
    }

    print("=== 📊 FINAL OUTPUT ===")
    print(json.dumps(final_output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    run_pipeline()
