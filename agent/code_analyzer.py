import os
import requests
import json
from typing import Dict, List, Any

class CodeAnalyzer:
    """基于 MiMo V2.5 的智能代码审查器"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("MIMO_API_KEY")
        self.base_url = "https://api.xiaomimimo.com/v1/chat/completions"
        self.token_usage = {"input": 0, "output": 0, "total": 0}
    
    def call_mimo_api(self, code_snippet: str, task_type: str = "review") -> dict:
        """调用 MiMo V2.5 推理模型 API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        prompts = {
            "review": f"请审查以下代码，识别技术债、重复代码、安全漏洞。返回 JSON: {{'issues': [{'type': '...', 'severity': 'high/medium/low', 'line': N, 'description': '...', 'suggestion': '...'}], 'score': 0-100}}\n代码:\n{code_snippet[:5000]}",
            "refactor": f"请重构以下代码：\n{code_snippet[:3000]}",
            "test": f"为以下代码生成 pytest 单元测试：\n{code_snippet[:3000]}"
        }
        payload = {
            "model": "mimo-v2.5-reasoning",
            "messages": [
                {"role": "system", "content": "你是专业的代码审查专家，专注于 Python/Java/Go 代码质量分析。"},
                {"role": "user", "content": prompts.get(task_type, prompts["review"])}
            ],
            "temperature": 0.2,
            "max_tokens": 2000
        }
        try:
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            usage = result.get('usage', {})
            self.token_usage["input"] += usage.get('prompt_tokens', 0)
            self.token_usage["output"] += usage.get('completion_tokens', 0)
            self.token_usage["total"] += self.token_usage["input"] + self.token_usage["output"]
            return {"success": True, "content": result['choices'][0]['message']['content'], "usage": usage}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def analyze_file(self, filepath: str) -> Dict[str, Any]:
        try:
            with open(filepath, encoding="utf-8") as f:
                code = f.read()
        except Exception as e:
            return {"error": f"读取失败：{str(e)}"}
        lines = len(code.splitlines())
        file_issues = []
        for i, line in enumerate(code.splitlines()):
            if "TODO" in line.upper():
                file_issues.append({"type": "todo", "severity": "low", "line": i+1, "description": "发现 TODO", "suggestion": "建议完成或移除"})
            if "FIXME" in line.upper():
                file_issues.append({"type": "FIXME", "severity": "medium", "line": i+1, "description": "发现 FIXME", "suggestion": "建议修复"})
        if self.api_key and lines > 10:
            mimo_result = self.call_mimo_api(code, "review")
            if mimo_result["success"]:
                try:
                    ai_issues = json.loads(mimo_result["content"])
                    file_issues.extend(ai_issues.get("issues", []))
                    file_score = ai_issues.get("score", 70)
                except:
                    file_score = 70
            else:
                file_score = 60
        else:
            file_score = 80 if not file_issues else 60
        return {
            "filename": os.path.basename(filepath), "lines": lines,
            "size_bytes": len(code.encode('utf-8')), "issues": file_issues,
            "issue_count": len(file_issues),
            "severity_breakdown": {
                "high": len([i for i in file_issues if i.get("severity") == "high"]),
                "medium": len([i for i in file_issues if i.get("severity") == "medium"]),
                "low": len([i for i in file_issues if i.get("severity") == "low"])
            },
            "quality_score": file_score, "ai_reviewed": bool(self.api_key and lines > 10)
        }
    
    def analyze_directory(self, path: str, languages: List[str] = None) -> Dict[str, Any]:
        languages = languages or [".py", ".java", ".go"]
        results = {"files": [], "total_files": 0, "total_lines": 0, "total_issues": 0, "avg_quality_score": 0, "token_usage": self.token_usage.copy()}
        all_scores = []
        for root, dirs, files in os.walk(path):
            for filename in files:
                ext = os.path.splitext(filename)[1]
                if ext in languages:
                    filepath = os.path.join(root, filename)
                    file_result = self.analyze_file(filepath)
                    results["files"].append(file_result)
                    results["total_files"] += 1
                    results["total_lines"] += file_result.get("lines", 0)
                    results["total_issues"] += file_result.get("issue_count", 0)
                    all_scores.append(file_result.get("quality_score", 0))
        results["avg_quality_score"] = round(sum(all_scores)/len(all_scores), 1) if all_scores else 0
        return results

def analyze_code(path):
    analyzer = CodeAnalyzer()
    results = analyzer.analyze_directory(path)
    simplified = {}
    for f in results["files"]:
        simplified[f["filename"]] = {"lines": f["lines"], "issues": f["issue_count"], "score": f["quality_score"]}
    return simplified