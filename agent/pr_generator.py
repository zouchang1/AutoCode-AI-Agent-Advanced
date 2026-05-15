def generate_pr(results, output_file):
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# 自动生成 PR 建议\n\n")
        for file, info in results.items():
            f.write(f"文件: {file}\n")
            f.write(f"行数: {info['lines']}, TODO 数量: {info['todos']}\n")
            f.write("建议: 请检查 TODO 注释并优化代码结构\n\n")