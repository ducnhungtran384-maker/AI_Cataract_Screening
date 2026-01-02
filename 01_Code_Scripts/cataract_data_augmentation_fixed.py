"""
白内障数据集增强与合并脚本（已修复版本）
功能：
1. 对数据集2中的白内障图像进行数据增强（301张 -> 2874张）
2. 合并数据集1和增强后的数据集2
3. 重命名所有图片为连续数字序列
"""

import os
import cv2
import numpy as np
from pathlib import Path
import shutil
from tqdm import tqdm
import random

# ==================== 配置路径 ====================
# 数据集1路径（白内障1038张，常规1074张）
DATA1_PATH = r"C:\Users\weirui\Desktop\AI_Test\test1\data1"

# 数据集2路径（白内障301张，常规2874张）
DATA2_PATH = r"C:\Users\weirui\Desktop\AI_Test\data2"

# 输出路径
OUTPUT_PATH = r"C:\Users\weirui\Desktop\AI_Test\output"

# 类别文件夹名称
CATARACT_FOLDER = "Cataract"
NORMAL_FOLDER = "Normal"


# ==================== 数据增强函数 ====================
def augment_image(image, aug_type):
    """
    对单张图像进行数据增强
    
    参数:
        image: 输入图像（numpy数组）
        aug_type: 增强类型（字符串）
    
    返回:
        增强后的图像
    """
    if aug_type == "flip_horizontal":
        # 水平翻转
        return cv2.flip(image, 1)
    
    elif aug_type == "flip_vertical":
        # 垂直翻转
        return cv2.flip(image, 0)
    
    elif aug_type == "rotate_90":
        # 旋转90度
        return cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
    
    elif aug_type == "rotate_180":
        # 旋转180度
        return cv2.rotate(image, cv2.ROTATE_180)
    
    elif aug_type == "rotate_270":
        # 旋转270度
        return cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
    
    elif aug_type == "brightness_up":
        # 增加亮度
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        hsv[:, :, 2] = np.clip(hsv[:, :, 2] * 1.2, 0, 255)
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    
    elif aug_type == "brightness_down":
        # 降低亮度
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        hsv[:, :, 2] = np.clip(hsv[:, :, 2] * 0.8, 0, 255)
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    
    elif aug_type == "contrast_up":
        # 增加对比度
        return cv2.convertScaleAbs(image, alpha=1.3, beta=0)
    
    elif aug_type == "contrast_down":
        # 降低对比度
        return cv2.convertScaleAbs(image, alpha=0.7, beta=0)
    
    elif aug_type == "zoom_in":
        # 轻微放大（中心裁剪后缩放回原尺寸）
        h, w = image.shape[:2]
        crop_size = int(min(h, w) * 0.9)
        start_h = (h - crop_size) // 2
        start_w = (w - crop_size) // 2
        cropped = image[start_h:start_h+crop_size, start_w:start_w+crop_size]
        return cv2.resize(cropped, (w, h))
    
    elif aug_type == "combo_1":
        # 组合增强：水平翻转 + 亮度增加
        img = cv2.flip(image, 1)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        hsv[:, :, 2] = np.clip(hsv[:, :, 2] * 1.1, 0, 255)
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    
    elif aug_type == "combo_2":
        # 组合增强：旋转90度 + 对比度增加
        img = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        return cv2.convertScaleAbs(img, alpha=1.2, beta=0)
    
    else:
        # 默认返回原图
        return image


def get_image_files(folder_path):
    """
    获取文件夹中的所有图片文件（修复版：避免重复）
    
    参数:
        folder_path: 文件夹路径
    
    返回:
        图片文件路径列表
    """
    if not os.path.exists(folder_path):
        return []
    
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp'}
    image_files = []
    
    # 遍历文件夹中的所有文件
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        # 检查是否为文件，并且扩展名是图片格式
        if os.path.isfile(file_path):
            ext = os.path.splitext(file)[1].lower()  # 转为小写比较
            if ext in image_extensions:
                image_files.append(file_path)
    
    return image_files


def augment_cataract_data(data2_cataract_path, target_count):
    """
    对数据集2的白内障图像进行数据增强
    
    参数:
        data2_cataract_path: 数据集2白内障图片文件夹路径
        target_count: 目标图片数量（2874张）
    
    返回:
        增强后的图像列表 [(image_array, original_filename, aug_type), ...]
    """
    print(f"\n{'='*50}")
    print(f"开始对数据集2的白内障图像进行数据增强...")
    print(f"{'='*50}")
    
    # 获取原始白内障图片
    original_images = get_image_files(data2_cataract_path)
    original_count = len(original_images)
    
    print(f"原始白内障图片数量: {original_count}")
    print(f"目标图片数量: {target_count}")
    print(f"需要增强生成: {target_count - original_count} 张图片")
    
    if original_count == 0:
        print("错误：没有找到白内障图片！")
        return []
    
    # 存储所有图片（包括原始图片和增强后的图片）
    all_images = []
    
    # 首先添加所有原始图片
    print("\n读取原始图片...")
    for img_path in tqdm(original_images, desc="读取原始图片"):
        img = cv2.imread(img_path)
        if img is not None:
            all_images.append((img, os.path.basename(img_path), "original"))
    
    # 计算需要生成的增强图片数量
    needed_count = target_count - len(all_images)
    
    # 定义数据增强类型
    aug_types = [
        "flip_horizontal", "flip_vertical",
        "rotate_90", "rotate_180", "rotate_270",
        "brightness_up", "brightness_down",
        "contrast_up", "contrast_down",
        "zoom_in", "combo_1", "combo_2"
    ]
    
    print(f"\n生成增强图片...")
    # 循环生成增强图片，直到达到目标数量
    generated_count = 0
    with tqdm(total=needed_count, desc="生成增强图片") as pbar:
        while generated_count < needed_count:
            # 随机选择一张原始图片
            img_path = random.choice(original_images)
            img = cv2.imread(img_path)
            
            if img is not None:
                # 随机选择增强方式
                aug_type = random.choice(aug_types)
                
                # 进行数据增强
                augmented_img = augment_image(img, aug_type)
                
                # 添加到列表
                all_images.append((augmented_img, os.path.basename(img_path), aug_type))
                generated_count += 1
                pbar.update(1)
    
    print(f"\n数据增强完成！总共生成 {len(all_images)} 张白内障图片")
    return all_images


def copy_and_collect_images(source_path, category):
    """
    收集指定类别的所有图片
    
    参数:
        source_path: 源文件夹路径
        category: 类别名称（Cataract 或 Normal）
    
    返回:
        图片数组列表 [(image_array, original_filename), ...]
    """
    images = []
    image_files = get_image_files(source_path)
    
    print(f"从 {source_path} 读取 {len(image_files)} 张 {category} 图片...")
    for img_path in tqdm(image_files, desc=f"读取{category}图片"):
        img = cv2.imread(img_path)
        if img is not None:
            images.append((img, os.path.basename(img_path)))
    
    return images


def merge_and_save_dataset():
    """
    主函数：合并数据集并保存
    """
    print("="*70)
    print(" "*20 + "白内障数据集处理程序")
    print("="*70)
    
    # 清空并重新创建输出文件夹
    if os.path.exists(OUTPUT_PATH):
        print(f"\n清空现有输出文件夹: {OUTPUT_PATH}")
        shutil.rmtree(OUTPUT_PATH)
    
    output_cataract_path = os.path.join(OUTPUT_PATH, CATARACT_FOLDER)
    output_normal_path = os.path.join(OUTPUT_PATH, NORMAL_FOLDER)
    
    os.makedirs(output_cataract_path, exist_ok=True)
    os.makedirs(output_normal_path, exist_ok=True)
    
    print(f"\n输出文件夹已创建:")
    print(f"  - {output_cataract_path}")
    print(f"  - {output_normal_path}")
    
    # ==================== 处理白内障图片 ====================
    print("\n" + "="*70)
    print("步骤 1: 处理白内障图片")
    print("="*70)
    
    # 1. 收集数据集1的白内障图片
    print("\n[1/4] 收集数据集1的白内障图片...")
    data1_cataract_path = os.path.join(DATA1_PATH, CATARACT_FOLDER)
    data1_cataract_images = copy_and_collect_images(data1_cataract_path, "Cataract (数据集1)")
    
    # 2. 对数据集2的白内障图片进行数据增强
    print("\n[2/4] 对数据集2的白内障图片进行数据增强...")
    data2_cataract_path = os.path.join(DATA2_PATH, CATARACT_FOLDER)
    
    # 首先获取数据集2的常规图片数量，作为目标数量
    data2_normal_path = os.path.join(DATA2_PATH, NORMAL_FOLDER)
    data2_normal_count = len(get_image_files(data2_normal_path))
    
    # 进行数据增强
    data2_cataract_images = augment_cataract_data(data2_cataract_path, data2_normal_count)
    
    # 3. 合并所有白内障图片
    print("\n[3/4] 合并所有白内障图片...")
    all_cataract_images = data1_cataract_images + data2_cataract_images
    print(f"白内障图片总数: {len(all_cataract_images)}")
    print(f"  - 数据集1: {len(data1_cataract_images)} 张")
    print(f"  - 数据集2（增强后）: {len(data2_cataract_images)} 张")
    
    # 4. 保存白内障图片（重命名为数字序列）
    print("\n[4/4] 保存白内障图片...")
    for idx, img_data in enumerate(tqdm(all_cataract_images, desc="保存白内障图片"), start=1):
        # 处理不同来源的图片数据
        if len(img_data) == 3:  # 来自数据增强的图片: (image_array, filename, aug_type)
            img_array = img_data[0]
            ext = os.path.splitext(img_data[1])[1]
        else:  # 来自数据集1的原始图片: (image_array, filename)
            img_array = img_data[0]
            ext = os.path.splitext(img_data[1])[1]
        
        # 新文件名：数字序列
        new_filename = f"{idx}{ext}"
        output_file = os.path.join(output_cataract_path, new_filename)
        
        # 保存图片
        cv2.imwrite(output_file, img_array)
    
    print(f"✓ 白内障图片保存完成！共 {len(all_cataract_images)} 张")
    
    # ==================== 处理常规图片 ====================
    print("\n" + "="*70)
    print("步骤 2: 处理常规图片")
    print("="*70)
    
    # 1. 收集数据集1的常规图片
    print("\n[1/3] 收集数据集1的常规图片...")
    data1_normal_path = os.path.join(DATA1_PATH, NORMAL_FOLDER)
    data1_normal_images = copy_and_collect_images(data1_normal_path, "Normal (数据集1)")
    
    # 2. 收集数据集2的常规图片
    print("\n[2/3] 收集数据集2的常规图片...")
    data2_normal_images = copy_and_collect_images(data2_normal_path, "Normal (数据集2)")
    
    # 3. 合并所有常规图片
    print("\n[3/3] 合并并保存常规图片...")
    all_normal_images = data1_normal_images + data2_normal_images
    print(f"常规图片总数: {len(all_normal_images)}")
    print(f"  - 数据集1: {len(data1_normal_images)} 张")
    print(f"  - 数据集2: {len(data2_normal_images)} 张")
    
    # 4. 保存常规图片（重命名为数字序列）
    for idx, (img, original_name) in enumerate(tqdm(all_normal_images, desc="保存常规图片"), start=1):
        # 获取原始文件扩展名
        ext = os.path.splitext(original_name)[1]
        
        # 新文件名：数字序列
        new_filename = f"{idx}{ext}"
        output_file = os.path.join(output_normal_path, new_filename)
        
        # 保存图片
        cv2.imwrite(output_file, img)
    
    print(f"✓ 常规图片保存完成！共 {len(all_normal_images)} 张")
    
    # ==================== 总结 ====================
    print("\n" + "="*70)
    print(" "*25 + "处理完成！")
    print("="*70)
    print(f"\n数据集统计:")
    print(f"  白内障图片: {len(all_cataract_images)} 张")
    print(f"    - 数据集1: {len(data1_cataract_images)} 张")
    print(f"    - 数据集2（增强后）: {len(data2_cataract_images)} 张")
    print(f"\n  常规图片:   {len(all_normal_images)} 张")
    print(f"    - 数据集1: {len(data1_normal_images)} 张")
    print(f"    - 数据集2: {len(data2_normal_images)} 张")
    print(f"\n  总计:       {len(all_cataract_images) + len(all_normal_images)} 张")
    print(f"\n输出位置:")
    print(f"  {OUTPUT_PATH}")
    print("\n所有图片已重命名为数字序列（1.jpg, 2.jpg, 3.jpg ...）")
    print("="*70)


# ==================== 主程序入口 ====================
if __name__ == "__main__":
    try:
        merge_and_save_dataset()
    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()
