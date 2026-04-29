from utils.llm import call_llm

def analyze_risk(diff):
    prompt = f"""
Analyze the following code changes:

{diff}

Output:
1. Risk level (low/medium/high)
2. Risk details
3. Affected modules
"""
    return call_llm(prompt)
