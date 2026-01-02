"""
数据集检查脚本 - 统计每个文件夹中的图片数量
"""

import os
from pathlib import Path

# 配置路径
DATA1_PATH = r"C:\Users\weirui\Desktop\AI_Test\test1\data1"
DATA2_PATH = r"C:\Users\weirui\Desktop\AI_Test\data2"
OUTPUT_PATH = r"C:\Users\weirui\Desktop\AI_Test\output"

def count_images(folder_path):
    """统计文件夹中的图片数量"""
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.JPG', '.JPEG', '.PNG', '.BMP']
    
    if not os.path.exists(folder_path):
        return 0, []
    
    files = []
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        if os.path.isfile(file_path) and any(file.endswith(ext) for ext in image_extensions):
            files.append(file)
    
    return len(files), files

print("="*70)
print(" "*20 + "数据集统计检查")
print("="*70)

# 检查数据集1
print("\n【数据集1】路径:", DATA1_PATH)
data1_cataract_path = os.path.join(DATA1_PATH, "Cataract")
data1_normal_path = os.path.join(DATA1_PATH, "Normal")

data1_cataract_count, _ = count_images(data1_cataract_path)
data1_normal_count, _ = count_images(data1_normal_path)

print(f"  Cataract: {data1_cataract_count} 张")
print(f"  Normal:   {data1_normal_count} 张")
print(f"  总计:     {data1_cataract_count + data1_normal_count} 张")

# 检查数据集2
print("\n【数据集2】路径:", DATA2_PATH)
data2_cataract_path = os.path.join(DATA2_PATH, "Cataract")
data2_normal_path = os.path.join(DATA2_PATH, "Normal")

data2_cataract_count, _ = count_images(data2_cataract_path)
data2_normal_count, _ = count_images(data2_normal_path)

print(f"  Cataract: {data2_cataract_count} 张")
print(f"  Normal:   {data2_normal_count} 张")
print(f"  总计:     {data2_cataract_count + data2_normal_count} 张")

# 检查输出文件夹
print("\n【输出文件夹】路径:", OUTPUT_PATH)
if os.path.exists(OUTPUT_PATH):
    output_cataract_path = os.path.join(OUTPUT_PATH, "Cataract")
    output_normal_path = os.path.join(OUTPUT_PATH, "Normal")
    
    output_cataract_count, _ = count_images(output_cataract_path)
    output_normal_count, _ = count_images(output_normal_path)
    
    print(f"  Cataract: {output_cataract_count} 张")
    print(f"  Normal:   {output_normal_count} 张")
    print(f"  总计:     {output_cataract_count + output_normal_count} 张")
else:
    print("  输出文件夹不存在")

# 检查是否有重复文件名
print("\n" + "="*70)
print("【检查数据集1中是否有重复文件名】")
data1_cataract_count, data1_cataract_files = count_images(data1_cataract_path)
data1_normal_count, data1_normal_files = count_images(data1_normal_path)

if len(data1_cataract_files) != len(set(data1_cataract_files)):
    print("⚠️ 数据集1 Cataract 文件夹有重复文件名！")
else:
    print("✓ 数据集1 Cataract 文件夹无重复文件名")

if len(data1_normal_files) != len(set(data1_normal_files)):
    print("⚠️ 数据集1 Normal 文件夹有重复文件名！")
else:
    print("✓ 数据集1 Normal 文件夹无重复文件名")

print("\n【检查数据集2中是否有重复文件名】")
data2_cataract_count, data2_cataract_files = count_images(data2_cataract_path)
data2_normal_count, data2_normal_files = count_images(data2_normal_path)

if len(data2_cataract_files) != len(set(data2_cataract_files)):
    print("⚠️ 数据集2 Cataract 文件夹有重复文件名！")
else:
    print("✓ 数据集2 Cataract 文件夹无重复文件名")

if len(data2_normal_files) != len(set(data2_normal_files)):
    print("⚠️ 数据集2 Normal 文件夹有重复文件名！")
else:
    print("✓ 数据集2 Normal 文件夹无重复文件名")

print("\n" + "="*70)
print("检查完成！")
print("="*70)
