import os

def analyze_code(path):
    analysis_results = {}
    for filename in os.listdir(path):
        if filename.endswith(".py"):
            with open(os.path.join(path, filename), encoding="utf-8") as f:
                code = f.read()
                analysis_results[filename] = {
                    "lines": len(code.splitlines()),
                    "todos": code.count("TODO")
                }
    return analysis_results