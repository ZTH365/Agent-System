from utils.git_utils import get_git_diff
from agents.risk_agent import analyze_risk
from agents.test_agent import generate_tests
from agents.rollback_agent import suggest_rollback

def run_pipeline():
    print("Starting Agent System...\n")

    diff = get_git_diff()
    if not diff.strip():
        print("No code changes detected")
        return

    print("Code change detected, analyzing...\n")

    risk = analyze_risk(diff)
    print("=== Risk Analysis ===")
    print(risk)
    print()

    tests = generate_tests(diff)
    print("=== Test Strategy ===")
    print(tests)
    print()

    rollback = suggest_rollback(diff)
    print("=== Rollback Suggestion ===")
    print(rollback)
    print()

if __name__ == "__main__":
    run_pipeline()
