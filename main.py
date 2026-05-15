#!/usr/bin/env python3
"""
AutoCode AI Agent - 智能代码审查与自动修复系统
基于 MiMo V2.5 推理模型驱动

Usage:
    python main.py [--api-key YOUR_KEY] [directory]
"""

import os
import sys
from datetime import datetime
from agent.code_analyzer import CodeAnalyzer
from agent.pr_generator import PRGenerator
from agent.test_runner import TestRunner

def main():
    # 解析命令行参数
    api_key = None
    target_dir = "demo_code/"
    
    for i, arg in enumerate(sys.argv[1:], 1):
        if arg == "--api-key" and i < len(sys.argv):
            api_key = sys.argv[i + 1]
        elif not arg.startswith("-"):
            target_dir = arg
    
    print(f"{'='*60}")
    print(" AutoCode AI Agent - 智能代码审查系统")
    print(f" 基于 MiMo V2.5 推理模型 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\\n")
    
    # 初始化组件
    analyzer = CodeAnalyzer(api_key)
    pr_gen = PRGenerator(api_key)
    test_runner = TestRunner(api_key)
    
    all_token_usage = {"input": 0, "output": 0}
    
    # 步骤 1：代码分析
    print(f"[1/3] 扫描目录：{target_dir}")
    results = analyzer.analyze_directory(target_dir)
    print(f"  - 发现 {results['total_files']} 个文件")
    print(f"  - 总行数：{results['total_lines']}")
    print(f"  - 发现问题：{results['total_issues']} 个")
    print(f"  - 平均质量分：{results['avg_quality_score']}/100\\n")
    
    # 保存详细分析结果
    analysis_output = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    import json
    with open(analysis_output, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"  -> 详细报告已保存：{analysis_output}\\n")
    
    # 保存为字典格式以兼容原有代码
    simplified_results = {}
    for file_info in results.get('files', []):
        simplified_results[file_info['filename']] = {
            'lines': file_info['lines'],
            'issues': file_info['issue_count'],
            'score': file_info['quality_score'],
            'ai_reviewed': file_info['ai_reviewed']
        }
    
    # 记录 Token 使用
    if hasattr(analyzer, 'token_usage'):
        all_token_usage["input"] += analyzer.token_usage.get("input", 0)
        all_token_usage["output"] += analyzer.token_usage.get("output", 0)
    
    # 步骤 2：生成 PR 建议
    print("[2/3] 生成 PR 建议...")
    pr_output = "suggested_pr.md"
    pr_gen.generate_pr(simplified_results, pr_output)
    print(f"  -> PR 建议已保存：{pr_output}\\n")
    
    # 步骤 3：运行测试
    print("[3/3] 执行自动化测试...")
    log_output = f"logs/agent_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    os.makedirs("logs", exist_ok=True)
    test_runner.run_tests(target_dir, log_output)
    print(f"  -> 测试日志已保存：{log_output}\\n")
    
    # 汇总 Token 统计
    print(f"{'='*60}")
    print(" Token 使用统计:")
    print(f"  - 输入 Token: {all_token_usage['input']:,}")
    print(f"  - 输出 Token: {all_token_usage['output']:,}")
    total = all_token_usage['input'] + all_token_usage['output']
    print(f"  - 总计：{total:,}")
    print(f"{'='*60}\\n")
    
    print("✅ 代码审查完成!\\n")
    return 0

if __name__ == "__main__":
    sys.exit(main())