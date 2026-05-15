import requests
import os
from datetime import datetime

class PRGenerator:
    """基于 MiMo V2.5 的自动 PR 建议生成器"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("MIMO_API_KEY")
        self.base_url = "https://api.xiaomimimo.com/v1/chat/completions"
        self.token_usage = {"input": 0, "output": 0}
    
    def call_mimo_api(self, analysis_results: dict) -> str:
        """调用 MiMo 生成 PR 建议"""
        if not self.api_key:
            return None
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        prompt = "根据以下代码分析结果，生成详细的 PR 建议:\n\n"
        for file, info in analysis_results.items() if isinstance(analysis_results, dict) else analysis_results.get('files', {}).items():
            prompt += f"文件:{file}\n问题数:{info.get('issue_count', 0)}\n评分:{info.get('quality_score', 0)}\n\n"
        prompt += "请给出重构建议和优先级排序。"
        payload = {
            "model": "mimo-v2.5-reasoning",
            "messages": [
                {"role": "system", "content": "你是资深代码审查专家，能给出专业的重构建议。"},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 3000
        }
        try:
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            usage = result.get('usage', {})
            self.token_usage["input"] += usage.get('prompt_tokens', 0)
            self.token_usage["output"] += usage.get('completion_tokens', 0)
            return result['choices'][0]['message']['content']
        except Exception as e:
            print(f"MiMo API 调用失败:{str(e)}")
            return None
    
    def generate_pr(self, results: dict, output_file: str):
        """生成 PR 建议文件"""
        ai_suggestion = self.call_mimo_api(results)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("# 自动生成 PR 建议\n")
            f.write(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            if ai_suggestion:
                f.write("## AI 驱动的代码审查建议 (MiMo V2.5)\n\n")
                f.write(ai_suggestion + "\n\n")
            else:
                f.write("## 基础分析结果\n\n")
                for file, info in results.items() if isinstance(results, dict) else results.get('files', {}).items():
                    f.write(f"### 文件:{file}\n")
                    f.write(f"- 行数:{info.get('lines', 0)}\n")
                    f.write(f"- 问题数:{info.get('issues', info.get('issue_count', 0))}\n")
                    f.write(f"- 质量评分:{info.get('score', info.get('quality_score', 0))}/100\n")
                    f.write(f"- AI 审查: {'是' if info.get('ai_reviewed') else '否'}\n\n")
                f.write("建议：请检查 TODO 注释并优化代码结构\n")

# 兼容旧版本
def generate_pr(results, output_file):
    generator = PRGenerator()
    generator.generate_pr(results, output_file)