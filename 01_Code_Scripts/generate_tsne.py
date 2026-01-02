import torch
import torch.nn as nn
from torchvision import datasets, models, transforms
from torch.utils.data import DataLoader
import os
import numpy as np
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import matplotlib

# 配置
MODEL_PATH = "../result/best_cataract_model.pth"
DATA_PATH = "../04data/ALL_Data_split12/Test"
OUTPUT_FILE = "../visualization/tsne_plot.png"

# 设置中文字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei'] 
matplotlib.rcParams['axes.unicode_minus'] = False

def generate_tsne():
    print("🚀 Starting t-SNE generation...")
    
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print(f"   Device: {device}")

    # 1. 准备数据
    if not os.path.exists(DATA_PATH):
        print(f"❌ Error: Dataset path not found: {DATA_PATH}")
        return

    data_transforms = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    
    dataset = datasets.ImageFolder(DATA_PATH, transform=data_transforms)
    dataloader = DataLoader(dataset, batch_size=32, shuffle=False)
    print(f"   Dataset: {len(dataset)} images")

    # 2. 加载模型
    print("   Loading model...")
    model = models.resnet18(weights=None)
    # 先恢复原来的结构加载权重
    model.fc = nn.Linear(model.fc.in_features, 2)
    try:
        model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
        print("   Weights loaded.")
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        return

    # 修改模型以提取特征 (移除最后一层分类器)
    # ResNet18 的 fc 层前是 avgpool，输出 512 维
    model.fc = nn.Identity() 
    model = model.to(device)
    model.eval()

    # 3. 提取特征
    print("   Extracting features...")
    all_features = []
    all_labels = []

    with torch.no_grad():
        for inputs, labels in dataloader:
            inputs = inputs.to(device)
            # 此时输出已经是 512 维特征向量
            features = model(inputs)
            
            all_features.append(features.cpu().numpy())
            all_labels.append(labels.cpu().numpy())

    all_features = np.concatenate(all_features, axis=0)
    all_labels = np.concatenate(all_labels, axis=0)
    
    print(f"   Feature shape: {all_features.shape}") # Should be (N, 512)

    # 4. t-SNE 降维
    print("   Running t-SNE (this might take a while)...")
    # n_jobs=1 to avoid Windows multiprocessing issues
    tsne = TSNE(n_components=2, random_state=42, init='pca', learning_rate='auto', n_jobs=1)
    X_embedded = tsne.fit_transform(all_features)
    print("   t-SNE complete.")

    # 5. 绘图
    print("   Plotting...")
    plt.figure(figsize=(10, 8), dpi=100)
    
    # 获取类别映射
    idx_to_class = {v: k for k, v in dataset.class_to_idx.items()}
    
    # 定义颜色和标签
    # 假设 0: Cataract, 1: Normal
    colors = ['#ff4d4f', '#1890ff'] # 红, 蓝
    labels_map = ['Cataract (白内障)', 'Normal (正常)']
    
    for i in range(2):
        # 筛选出属于该类别的索引
        indices = all_labels == i
        plt.scatter(
            X_embedded[indices, 0], 
            X_embedded[indices, 1], 
            c=colors[i], 
            label=labels_map[i],
            alpha=0.6,
            s=20
        )

    plt.title('t-SNE Feature Visualization (ResNet18)', fontsize=16)
    plt.legend(loc='best')
    plt.grid(True, alpha=0.3)
    
    # 调整布局，为底部解释留出空间
    plt.subplots_adjust(bottom=0.25)

    # 添加图解指南 (放在底部空白处)
    explanation_text = (
        "【图表解读指南】\n"
        "● 点的位置：代表图片在AI眼中的特征相似度\n"
        "● 距离含义：点靠得越近，说明图片长得越像\n"
        "● 理想状态：红蓝两色泾渭分明，无混杂\n"
        "● 关键关注：混入对方阵营的点 = AI容易看错的疑难杂症"
    )
    # 在Figure坐标系下添加文本
    plt.figtext(0.05, 0.02, explanation_text, fontsize=9, 
                verticalalignment='bottom', horizontalalignment='left',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='#f8f9fa', alpha=0.9, edgecolor='#ddd'),
                fontname='SimHei')
    
    # 保存
    if not os.path.exists("../visualization"):
        os.makedirs("../visualization")
        
    plt.savefig(OUTPUT_FILE)
    print(f"✅ t-SNE plot saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_tsne()
