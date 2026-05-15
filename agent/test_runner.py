import subprocess

def run_tests(path, log_file):
    with open(log_file, "w", encoding="utf-8") as f:
        try:
            subprocess.run(["pytest", path], stdout=f, stderr=f, check=True)
        except FileNotFoundError:
            f.write("pytest 未安装，请执行: pip install pytest\n")