with open('visualization/js/data.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"原文件总行数: {len(lines)}")

# 删除第 6-44 行（索引 5-43）
# 保留第 1-5 行和第 45+ 行
new_lines = lines[:5] + lines[44:]

print(f"新文件总行数: {len(new_lines)}")

# 写入
with open('visualization/js/data.js', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("✅ 已删除第一个 PyTorch_ResNet 条目（第 6-44 行）")
