import os
import time
import logging
from typing import Optional, List, Dict
from openai import OpenAI

# ========================
# 基础配置
# ========================
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ========================
# 工具函数
# ========================
def truncate_text(text: str, max_chars: int = 12000) -> str:
    """防止 prompt 过长"""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n\n... (truncated)"


# ========================
# 核心调用函数
# ========================
def call_llm(
    prompt: str,
    temperature: float = 0.2,
    model: str = "gpt-4o-mini",
    max_retries: int = 3,
    timeout: int = 30
) -> str:
    """
    LLM 调用封装（生产级）

    特性：
    - 自动重试
    - 超时控制
    - prompt 裁剪
    - 日志记录
    """

    prompt = truncate_text(prompt)

    messages: List[Dict] = [
        {"role": "user", "content": prompt}
    ]

    for attempt in range(max_retries):
        try:
            start = time.time()

            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                timeout=timeout
            )

            duration = round(time.time() - start, 2)

            content = response.choices[0].message.content

            logger.info(f"LLM call success | model={model} | time={duration}s")

            return content

        except Exception as e:
            logger.warning(f"LLM call failed (attempt {attempt+1}): {str(e)}")

            if attempt == max_retries - 1:
                return f"[LLM ERROR] {str(e)}"

            # 指数退避
            time.sleep(2 ** attempt)


# ========================
# 可选：结构化输出
# ========================
def call_llm_json(
    prompt: str,
    temperature: float = 0.2
) -> dict:
    """
    强制返回 JSON（用于 Agent）
    """

    prompt = f"""
请严格返回 JSON，不要包含解释：

{prompt}
"""

    result = call_llm(prompt, temperature=temperature)

    import json
    try:
        return json.loads(result)
    except:
        return {
            "error": "invalid_json",
            "raw_output": result
        }
