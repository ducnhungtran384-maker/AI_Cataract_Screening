import os
import shutil
import random
from pathlib import Path
from typing import List, Tuple, Dict

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False
    print("💡 提示：安装 tqdm 可以显示进度条 (pip install tqdm)")

# ==================== 配置区域 ====================
# 源数据文件夹
SOURCE_ROOT = "output"
# 目标输出文件夹
DEST_ROOT = "Split_Data"

# 数据集划分比例
TRAIN_RATIO = 0.8   # 训练集 80%
TEST_RATIO = 0.2    # 测试集 20%

# 分类列表
CLASSES = ["Normal", "Cataract"]

# 随机种子（确保结果可重复，改成其他数字会得到不同的划分）
RANDOM_SEED = 42

# 支持的图像格式
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.gif'}

# ==================================================


def is_image_file(filename: str) -> bool:
    """检查文件是否为图像文件"""
    return Path(filename).suffix.lower() in IMAGE_EXTENSIONS


def get_image_files(directory: str) -> List[str]:
    """获取目录下所有图像文件"""
    all_files = os.listdir(directory)
    image_files = [f for f in all_files if is_image_file(f)]
    
    non_image_count = len(all_files) - len(image_files)
    if non_image_count > 0:
        print(f"   ⚠️  跳过 {non_image_count} 个非图像文件")
    
    return image_files


def split_data(images: List[str]) -> Tuple[List[str], List[str]]:
    """将图像列表按比例分割成训练集和测试集"""
    total = len(images)
    
    train_count = int(total * TRAIN_RATIO)
    
    train_images = images[:train_count]
    test_images = images[train_count:]
    
    return train_images, test_images


def copy_files(source_dir: str, dest_dir: str, file_list: List[str], 
               desc: str = "复制文件") -> Tuple[int, int]:
    """
    复制文件列表到目标目录
    返回：(成功数量, 失败数量)
    """
    os.makedirs(dest_dir, exist_ok=True)
    
    success_count = 0
    error_count = 0
    
    # 使用进度条或简单输出
    iterator = tqdm(file_list, desc=desc, ncols=80) if HAS_TQDM else file_list
    
    for filename in iterator:
        try:
            src_path = os.path.join(source_dir, filename)
            dst_path = os.path.join(dest_dir, filename)
            shutil.copy2(src_path, dst_path)  # copy2 保留元数据
            success_count += 1
        except Exception as e:
            error_count += 1
            if not HAS_TQDM:
                print(f"   ❌ 复制失败 {filename}: {e}")
    
    return success_count, error_count


def print_statistics(stats: Dict[str, Dict[str, int]]):
    """打印统计信息"""
    print("\n" + "="*60)
    print("📊 数据集划分统计")
    print("="*60)
    
    for class_name, class_stats in stats.items():
        print(f"\n【{class_name}】")
        print(f"  ├─ 训练集: {class_stats['train']:>4} 张 ({TRAIN_RATIO*100:.0f}%)")
        print(f"  ├─ 测试集: {class_stats['test']:>4} 张 ({TEST_RATIO*100:.0f}%)")
        print(f"  └─ 总计:   {class_stats['total']:>4} 张")
    
    # 总体统计
    total_train = sum(s['train'] for s in stats.values())
    total_test = sum(s['test'] for s in stats.values())
    total_all = sum(s['total'] for s in stats.values())
    
    print(f"\n【总计】")
    print(f"  ├─ 训练集: {total_train:>4} 张")
    print(f"  ├─ 测试集: {total_test:>4} 张")
    print(f"  └─ 总计:   {total_all:>4} 张")
    print("="*60)


def split_dataset():
    """主函数：执行数据集划分"""
    
    # 设置随机种子
    random.seed(RANDOM_SEED)
    print(f"🎲 随机种子: {RANDOM_SEED} (可在代码中修改以获得不同划分)")
    
    # 检查目标文件夹是否存在
    if os.path.exists(DEST_ROOT):
        print(f"\n⚠️  警告：检测到 '{DEST_ROOT}' 文件夹已存在！")
        user_input = input("是否删除并重新创建？(y/n): ").strip().lower()
        if user_input == 'y':
            shutil.rmtree(DEST_ROOT)
            print(f"✅ 已删除 '{DEST_ROOT}'")
        else:
            print("❌ 操作取消，程序退出")
            return
    
    # 检查源文件夹
    if not os.path.exists(SOURCE_ROOT):
        print(f"❌ 错误：源文件夹 '{SOURCE_ROOT}' 不存在！")
        return
    
    print(f"\n📁 源文件夹: {SOURCE_ROOT}")
    print(f"📁 目标文件夹: {DEST_ROOT}")
    print(f"📊 划分比例: 训练集 {TRAIN_RATIO*100:.0f}% | 测试集 {TEST_RATIO*100:.0f}%\n")
    
    statistics = {}
    total_errors = 0
    
    # 处理每个类别
    for class_name in CLASSES:
        source_dir = os.path.join(SOURCE_ROOT, class_name)
        
        if not os.path.exists(source_dir):
            print(f"⚠️  跳过：{class_name} (文件夹不存在)")
            continue
        
        print(f"\n{'='*60}")
        print(f"📂 处理类别: {class_name}")
        print(f"{'='*60}")
        
        # 获取图像文件
        images = get_image_files(source_dir)
        
        if len(images) == 0:
            print(f"   ⚠️  该类别没有图像文件，跳过")
            continue
        
        # 随机打乱
        random.shuffle(images)
        
        # 划分数据
        train_images, test_images = split_data(images)
        
        print(f"   总计: {len(images)} 张")
        print(f"   ├─ 训练集: {len(train_images)} 张")
        print(f"   └─ 测试集: {len(test_images)} 张\n")
        
        # 创建目标目录并复制文件
        train_dir = os.path.join(DEST_ROOT, "Train", class_name)
        test_dir = os.path.join(DEST_ROOT, "Test", class_name)
        
        train_success, train_error = copy_files(source_dir, train_dir, train_images, f"   训练集 - {class_name}")
        test_success, test_error = copy_files(source_dir, test_dir, test_images, f"   测试集 - {class_name}")
        
        # 统计
        statistics[class_name] = {
            'train': train_success,
            'test': test_success,
            'total': train_success + test_success
        }
        
        total_errors += train_error + test_error
        
        if train_error + test_error > 0:
            print(f"   ⚠️  有 {train_error + test_error} 个文件复制失败")
    
    # 打印统计信息
    if statistics:
        print_statistics(statistics)
        
        if total_errors > 0:
            print(f"\n⚠️  总计 {total_errors} 个文件复制失败")
        
        print(f"\n✨ 完成！数据集已保存到: {DEST_ROOT}")
        print(f"📁 目录结构:")
        print(f"   {DEST_ROOT}/")
        print(f"   ├── Train/    (训练集)")
        print(f"   └── Test/     (测试集)")
    else:
        print("\n❌ 没有处理任何数据")


if __name__ == "__main__":
    split_dataset()