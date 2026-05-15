import subprocess
import os
import requests
from datetime import datetime

class TestRunner:
    """基于 MiMo V2.5 的自动测试生成与运行器"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("MIMO_API_KEY")
        self.base_url = "https://api.xiaomimimo.com/v1/chat/completions"
        self.token_usage = {"input": 0, "output": 0}
    
    def call_mimo_api(self, code: str) -> str:
        """调用 MiMo 生成单元测试"""
        if not self.api_key:
            return None
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        prompt = f"为以下 Python 代码生成完整的 pytest 单元测试，覆盖所有边界情况和异常处理:\n\n{code[:2000]}\n\n请以完整可运行的测试文件形式返回。"
        payload = {
            "model": "mimo-v2.5-reasoning",
            "messages": [
                {"role": "system", "content": "你是专业的测试开发工程师，擅长编写全面的单元测试。"},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 4000
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
    
    def generate_tests(self, source_file: str) -> str:
        """为源文件生成测试用例"""
        try:
            with open(source_file, encoding="utf-8") as f:
                code = f.read()
        except Exception as e:
            return f"# 读取失败：{str(e)}"
        
        ai_test = self.call_mimo_api(code)
        if ai_test:
            # 提取 markdown 代码块
            if "```python" in ai_test:
                start = ai_test.find("```python") + 9
                end = ai_test.find("```", start)
                ai_test = ai_test[start:end].strip()
            return ai_test
        return None
    
    def run_tests(self, path: str, log_file: str):\
        """执行测试并记录结果"""
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(f"# AI 自动测试报告 - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            
            # 尝试运行 pytest
            try:
                result = subprocess.run(
                    ["pytest", "--tb=short", "-v", path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=120
                )
                f.write("## 测试结果\n\n")
                f.write(f"{'通过' if result.returncode == 0 else '失败'}\n\n")
                f.write("```\\n")
                f.write(result.stdout + result.stderr)
                f.write("\\n```\n")
                
                # 解析覆盖率统计
                if "passed" in result.stdout:
                    for line in result.stdout.split('\\n'):
                        if "passed" in line or "failed" in line or "error" in line.lower():
                            f.write(f"{line.strip()}\\n")
                
            except FileNotFoundError:
                f.write("## 错误\\n\\n")
                f.write("pytest 未安装，请执行：pip install pytest\\n")
            except subprocess.TimeoutExpired:
                f.write("## 超时\\n\\n")
                f.write("测试执行超时 (120 秒)\\n")
            
            # Token 使用统计
            f.write("\\n\\n## Token 使用统计\\n\\n")
            if hasattr(self, 'token_usage'):
                f.write(f"输入 Token: {self.token_usage['input']}\\n")
                f.write(f"输出 Token: {self.token_usage['output']}\\n")
                f.write(f"总计：{self.token_usage['input'] + self.token_usage['output']}\\n")

# 兼容旧版本
def run_tests(path, log_file):
    runner = TestRunner()
    runner.run_tests(path, log_file)