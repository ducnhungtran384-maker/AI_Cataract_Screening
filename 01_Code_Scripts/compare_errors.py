import re

# 读取旧的备份
with open('visualization/js/error_data_backup_23cases.js', 'r', encoding='utf-8') as f:
    old_content = f.read()
old_files = set(re.findall(r'"filename":\s*"([^"]+)"', old_content))
print(f"📦 旧数据（finalmodel）: {len(old_files)} 张")
print("文件列表:")
for f in sorted(old_files):
    print(f"  - {f}")

# 读取新的
with open('visualization/js/error_data.js', 'r', encoding='utf-8') as f:
    new_content = f.read()
new_files_prefixed = set(re.findall(r'"filename":\s*"([^"]+)"', new_content))

# 去掉前缀（cataract_ 或 normal_）
new_files = set()
for f in new_files_prefixed:
    if f.startswith('cataract_'):
        new_files.add(f.replace('cataract_', ''))
    elif f.startswith('normal_'):
        new_files.add(f.replace('normal_', ''))
    else:
        new_files.add(f)

print(f"\n🆕 新数据（PyTorch）: {len(new_files)} 张（去前缀后）")

# 找重叠
overlap = old_files & new_files
print(f"\n🔄 重叠图片: {len(overlap)} 张")
if overlap:
    print("重叠列表:")
    for f in sorted(overlap):
        print(f"  ✓ {f}")

# 找差异
only_old = old_files - new_files
only_new = new_files - old_files

print(f"\n📌 只在旧数据中: {len(only_old)} 张")
if only_old:
    for f in sorted(only_old):
        print(f"  - {f}")

print(f"\n🆕 只在新数据中: {len(only_new)} 张")
if only_new:
    for f in sorted(only_new):
        print(f"  + {f}")

print(f"\n📊 总结:")
print(f"  重叠率: {len(overlap)/len(old_files)*100:.1f}% ({len(overlap)}/{len(old_files)})")
print(f"  新增案例: {len(only_new)} 张")
