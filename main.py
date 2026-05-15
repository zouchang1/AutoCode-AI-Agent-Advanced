from agent.code_analyzer import analyze_code
from agent.pr_generator import generate_pr
from agent.test_runner import run_tests

if __name__ == "__main__":
    results = analyze_code("demo_code/")
    print("分析结果:", results)
    generate_pr(results, "suggested_pr.md")
    print("PR 建议已生成: suggested_pr.md")
    run_tests("demo_code/", "logs/agent_log.txt")
    print("测试执行完成，日志保存在 logs/agent_log.txt")