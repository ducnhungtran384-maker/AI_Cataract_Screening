import os
import matplotlib.pyplot as plt
from PIL import Image

# 错误案例列表 (文件名, 真实类别, AI预测, 置信度)
errors = [
    ("372.png", "Cataract", "Normal", "100.00%"),
    ("2356.jpg", "Cataract", "Normal", "99.95%"),
    ("1242.jpg", "Normal", "Cataract", "99.93%"),
    ("1211.jpg", "Normal", "Cataract", "99.93%"),
    ("3874.jpg", "Cataract", "Normal", "99.76%"),
    ("1580.jpg", "Normal", "Cataract", "99.74%")
]

# 测试集的基础路径 (根据之前的 find_by_name 结果)
base_path = r"c:\Users\weirui\Desktop\AI_Test\Split_Data\Test"

def find_image_path(filename, label):
    # 根据类别在对应的子文件夹中查找图片
    path = os.path.join(base_path, label, filename)
    if os.path.exists(path):
        return path
    return None

# 设置绘图
plt.figure(figsize=(15, 10))
plt.rcParams['font.sans-serif'] = ['SimHei'] # 设置中文字体
plt.rcParams['axes.unicode_minus'] = False

for i, (fname, true_label, pred_label, conf) in enumerate(errors):
    img_path = find_image_path(fname, true_label)
    
    plt.subplot(2, 3, i + 1)
    if img_path:
        img = Image.open(img_path)
        plt.imshow(img)
        title_color = 'red'
        plt.title(f"文件名: {fname}\n真实: {true_label} | 预测: {pred_label}\n置信度: {conf}", color=title_color)
    else:
        plt.text(0.5, 0.5, f"未找到图片:\n{fname}", ha='center', va='center')
    plt.axis('off')

plt.tight_layout()
output_path = r"c:\Users\weirui\Desktop\AI_Test\error_analysis.png"
plt.savefig(output_path)
print(f"分析图已保存至: {output_path}")
plt.show()
