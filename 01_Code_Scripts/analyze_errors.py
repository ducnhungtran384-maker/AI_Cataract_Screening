import pandas as pd
import os
import shutil

# 读取数据
df = pd.read_excel(r'C:\Users\weirui\Desktop\AI_Test\chartdata\finalmodel.xlsx')

# 筛选错判案例
errors = df[df['真实类别'] != df['AI预测']]

print(f'总样本数: {len(df)}')
print(f'错判数量: {len(errors)}')
print(f'\n所有错判案例:')
print('='*80)

# 图片源目录
test_dir = r'C:\Users\weirui\Desktop\AI_Test\test1\Test'
cataract_dir = os.path.join(test_dir, 'Cataract')
normal_dir = os.path.join(test_dir, 'Normal')

# 目标目录
error_images_dir = r'C:\Users\weirui\Desktop\AI_Test\visualization\error_images'
os.makedirs(error_images_dir, exist_ok=True)

error_list = []

for idx, row in errors.iterrows():
    filename = row['文件名']
    true_label = row['真实类别']
    pred_label = row['AI预测']
    confidence = row['置信度']
    
    print(f"{filename}\t真实:{true_label}\t预测:{pred_label}\t置信度:{confidence:.4f}")
    
    # 根据真实类别确定源路径
    if true_label == 'Cataract':
        source_path = os.path.join(cataract_dir, filename)
    else:
        source_path = os.path.join(normal_dir, filename)
    
    # 检查文件是否存在
    if os.path.exists(source_path):
        # 复制到error_images目录
        dest_path = os.path.join(error_images_dir, filename)
        shutil.copy2(source_path, dest_path)
        print(f"  ✓ 已复制: {filename}")
        
        error_list.append({
            'filename': filename,
            'true_label': true_label,
            'pred_label': pred_label,
            'confidence': float(confidence),
            'image_path': f'error_images/{filename}'
        })
    else:
        print(f"  ✗ 文件不存在: {source_path}")

print(f'\n成功复制 {len(error_list)} 张错判图片到 visualization/error_images/')

# 生成 JSON 数据
import json
with open(r'C:\Users\weirui\Desktop\AI_Test\visualization\js\error_data.js', 'w', encoding='utf-8') as f:
    f.write('const ERROR_CASES = ')
    json.dump(error_list, f, ensure_ascii=False, indent=2)
    f.write(';')

print(f'已生成 error_data.js')
