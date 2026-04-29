import json
import logging
from typing import Dict, Any, Optional
from utils.llm import call_llm  # 假设这是你自己封装的底层调用

# 配置基础日志，方便流水线追踪
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_tests(diff: str, commit_msg: str = "") -> Optional[Dict[str, Any]]:
    """
    基于代码变更 (diff) 生成结构化的测试策略。
    
    Args:
        diff (str): Git diff 内容。
        commit_msg (str, optional): 相关的 Commit 信息，提供业务上下文。
        
    Returns:
        dict: 解析后的 JSON 格式测试策略，如果失败则返回 None。
    """
    if not diff or not diff.strip():
        logger.warning("⚠️ Diff 内容为空，跳过测试策略生成。")
        return None

    # 1. 优化 Prompt：加入专家人设、上下文限制和严格的 JSON 结构要求
    prompt = f"""
    你是一个资深的测试开发工程师 (QA/SDET)。请根据以下代码变更内容，制定详细且具有针对性的测试策略。
    
    【上下文信息】
    Commit Message: {commit_msg if commit_msg else "未提供"}
    
    【代码变更 (Git Diff)】
    ```diff
    {diff}
    ```
    
    【输出严格要求】
    请务必只返回一个合法的 JSON 对象，不要包含任何 Markdown 代码块标记（如 ```json）或其他说明性闲聊文字。
    必须严格遵循以下 JSON 格式：
    {{
        "test_types": ["列出需要的测试类型，例如: 单元测试、接口测试、UI测试"],
        "key_test_cases": [
            {{"title": "用例1标题", "description": "具体验证的核心逻辑A"}},
            {{"title": "用例2标题", "description": "具体验证的核心逻辑B"}}
        ],
        "edge_cases": [
            {{"scenario": "边界/异常场景1", "risk": "可能导致的系统异常说明"}},
            {{"scenario": "并发/极值场景2", "risk": "可能导致的系统异常说明"}}
        ],
        "suggested_tools": ["建议使用的测试框架，例如: pytest, JUnit, Postman"]
    }}
    """

    try:
        logger.info("🤖 正在呼叫 QA Agent 分析代码并生成测试策略...")
        
        # 2. 调用 LLM
        response_text = call_llm(prompt)
        
        # 3. 鲁棒性处理：清理 LLM 偶尔不听话带上的 Markdown 标记
        clean_text = response_text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        elif clean_text.startswith("```"):
            clean_text = clean_text[3:]
            
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]
            
        # 4. 解析为 Python 字典并返回
        strategy_json = json.loads(clean_text.strip())
        logger.info("✅ 测试策略生成成功！")
        return strategy_json
        
    except json.JSONDecodeError as e:
        logger.error(f"❌ 解析 JSON 失败！LLM 返回的格式不规范。错误: {e}")
        logger.debug(f"LLM 原始返回内容:\n{response_text}")
        return None
    except Exception as e:
        logger.error(f"❌ 生成测试策略时发生未知异常: {e}")
        return None

# ================= 测试运行 =================
if __name__ == "__main__":
    # 模拟一段 Diff
    sample_diff = """
    @@ -15,5 +15,9 @@ def calculate_discount(price, user_type):
         if user_type == 'VIP':
             return price * 0.8
    +    if price < 0:
    +        raise ValueError("价格不能为负数")
         return price
    """
    
    result = generate_tests(sample_diff, commit_msg="fix: 修复价格计算允许负数的漏洞")
    
    if result:
        print("\n最终输出的结构化数据:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
