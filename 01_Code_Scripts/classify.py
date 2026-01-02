import pandas as pd
import os
import shutil

def sort_images_by_folder_first(excel_path, images_source_folder, output_base_folder):
    print("=== 模式：遍历文件夹，反查Excel (自动跳过无记录图片) ===")

    # 1. 先把 Excel 读进内存，做成一个“字典”，这样查找速度极快
    # 字典结构：{'1000_left.jpg': 'cataract', '1000_right.jpg': 'normal fundus', ...}
    print(f"正在读取表格并建立索引: {excel_path}")
    
    if not os.path.exists(excel_path):
        print("错误：找不到 Excel 文件！")
        return

    try:
        df = pd.read_excel(excel_path)
    except Exception as e:
        print(f"表格读取出错: {e}")
        return

    # 创建查找字典
    diag_dict = {}
    for index, row in df.iterrows():
        # 把左眼文件名和诊断放入字典
        l_name = str(row['Left-Fundus'])
        l_diag = str(row['Left-Diagnostic Keywords']).lower()
        diag_dict[l_name] = l_diag
        
        # 把右眼文件名和诊断放入字典
        r_name = str(row['Right-Fundus'])
        r_diag = str(row['Right-Diagnostic Keywords']).lower()
        diag_dict[r_name] = r_diag

    print(f"索引建立完成！表格中包含 {len(diag_dict)} 条图片记录。")

    # 2. 准备输出文件夹
    normal_dir = os.path.join(output_base_folder, 'Normal')
    cataract_dir = os.path.join(output_base_folder, 'Cataract')
    os.makedirs(normal_dir, exist_ok=True)
    os.makedirs(cataract_dir, exist_ok=True)

    # 3. 遍历文件夹里的图片
    if not os.path.exists(images_source_folder):
        print("错误：源图片文件夹不存在！")
        return

    files = os.listdir(images_source_folder)
    print(f"开始扫描文件夹中的 {len(files)} 个文件...")

    count_normal = 0
    count_cataract = 0
    count_skipped = 0 # 表格里没有记录，或者不匹配后缀
    count_ignored = 0 # 既不是白内障也不是正常的其他病

    for i, filename in enumerate(files):
        # 只处理图片
        if not filename.lower().endswith(('.jpg', '.png', '.jpeg', '.tif')):
            continue

        # 核心逻辑：去字典里查这个文件名
        # dict.get(key) 如果找不到会返回 None，不会报错
        diag_result = diag_dict.get(filename)

        if diag_result:
            # === 如果在 Excel 里找到了这个文件名 ===
            
            target_path = None
            
            # 判断病症
            if 'cataract' in diag_result:
                target_path = cataract_dir
                count_cataract += 1
            elif 'normal fundus' in diag_result:
                target_path = normal_dir
                count_normal += 1
            else:
                count_ignored += 1 # 找到了，但是是其他病（如青光眼），跳过
            
            # 执行复制
            if target_path:
                src = os.path.join(images_source_folder, filename)
                dst = os.path.join(target_path, filename)
                shutil.copy2(src, dst)
        
        else:
            # === 如果 Excel 里根本没有这个文件名 ===
            count_skipped += 1
            # 这里静默跳过，什么都不做
        
        # 进度条
        if (i + 1) % 500 == 0:
            print(f"已扫描 {i + 1} 个文件...")

    # 4. 结果汇报
    print("-" * 30)
    print("任务结束！")
    print(f"  [√] 归入 Normal (正常): {count_normal}")
    print(f"  [√] 归入 Cataract (白内障): {count_cataract}")
    print(f"  [-] 其他病症 (忽略): {count_ignored}")
    print(f"  [!] Excel中未找到记录 (跳过): {count_skipped}")
    print("-" * 30)
    
    if count_normal == 0 and count_cataract == 0:
        print("小七提示：结果依然是 0？")
        print("这意味着你文件夹里的文件名（比如 1000_left.jpg）在 Excel 里完全找不到对应记录。")
        print("请检查是不是 Excel 数据不全，或者文件名后缀 (.jpg/.png) 不一致。")
    else:
        print(f"文件已保存至: {output_base_folder}")

# ==========================================
# 路径修改区
# ==========================================
excel_path = r"C:\Users\weirui\Desktop\AI_Test\data.xlsx" 
images_source = r"C:\Users\weirui\Desktop\AI_Test\All_Images"
output_folder = r"C:\Users\weirui\Desktop\AI_Test\Sorted_Dataset"

if __name__ == '__main__':
    sort_images_by_folder_first(excel_path, images_source, output_folder)