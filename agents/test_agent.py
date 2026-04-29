from utils.llm import call_llm

def generate_tests(diff):
    prompt = f"""
Based on the following code changes, generate test strategy:

{diff}

Output:
1. Test types
2. Key test cases
3. Edge cases
"""
    return call_llm(prompt)
