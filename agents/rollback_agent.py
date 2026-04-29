from utils.llm import call_llm

def suggest_rollback(diff):
    prompt = f"""
Given the following code changes, suggest rollback plan:

{diff}

Output:
1. Is rollback needed
2. Rollback steps
3. Data consistency risks
"""
    return call_llm(prompt)
