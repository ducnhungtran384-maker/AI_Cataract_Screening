import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, models, transforms
from torch.utils.data import DataLoader
import matplotlib.pyplot as plt
import os
import numpy as np

# ==========================================
# 队友专用：白内障 AI 训练模板 (PyTorch 版)
# ==========================================

# 1. 基础配置 (在这里修改路径)
DATA_PATH = "Split_Data/Split_Data/Train"  # 请确保文件夹内有 'cataract' 和 'normal' 两个子文件夹
BATCH_SIZE = 16
EPOCHS = 10
LEARNING_RATE = 0.001
SAVE_PATH = "best_cataract_model.pth"

def train_model():
    print(f"正在准备数据...")

    # 2. 数据增强 (你的功劳点：医疗影像优化)
    data_transforms = {
        'train': transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.RandomHorizontalFlip(),
            transforms.RandomRotation(15),
            transforms.ColorJitter(brightness=0.1, contrast=0.1),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ]),
        'val': transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ]),
    }

    # 加载数据集
    if not os.path.exists(DATA_PATH):
        print(f"错误：找不到路径 {DATA_PATH}，请先准备好数据集文件夹！")
        return

    full_dataset = datasets.ImageFolder(DATA_PATH, data_transforms['train'])

    # 划分训练集和验证集 (80% 训练, 20% 验证)
    train_size = int(0.8 * len(full_dataset))
    val_size = len(full_dataset) - train_size
    train_dataset, val_dataset = torch.utils.data.random_split(full_dataset, [train_size, val_size])

    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)

    print(f"数据集载入成功：训练集 {train_size} 张，验证集 {val_size} 张")
    print(f"标签对应关系: {full_dataset.class_to_idx}")

    # 3. 构建模型 (设备自动选择)
    if torch.cuda.is_available():
        device = torch.device("cuda:0")
        print(f"🚀 [检测成功] 已成功调用 NVIDIA 显卡进行加速训练！")
    else:
        device = torch.device("cpu")
        print(f"ℹ️ [检测提示] 未检测到显卡加速库，将使用 CPU 训练。")
        print(f"   (注：若要开启显卡加速，需安装 2.8G 的 CUDA 驱动包，但这并非必须，CPU 也能完成任务)")

    print(f"当前运行设备: {device}")

    # 使用 ResNet18 预训练模型
    model = models.resnet18(pretrained=True)
    num_ftrs = model.fc.in_features
    # 修改输出层为 2 类 (Cataract vs Normal)
    model.fc = nn.Linear(num_ftrs, 2)
    model = model.to(device)

    # 4. 定义优化器和损失函数
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

    # 5. 开始训练
    print("\n--- 训练正式开始 ---")
    best_acc = 0.0

    # 记录数据用于画图
    history = {'train_loss': [], 'val_acc': []}

    for epoch in range(EPOCHS):
        model.train()
        running_loss = 0.0

        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)

            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * inputs.size(0)

        epoch_loss = running_loss / train_size
        history['train_loss'].append(epoch_loss)

        # 验证模型
        model.eval()
        correct = 0
        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                _, preds = torch.max(outputs, 1)
                correct += torch.sum(preds == labels.data)

        epoch_acc = correct.double() / val_size
        history['val_acc'].append(epoch_acc.item())

        print(f"Epoch {epoch+1}/{EPOCHS} | Loss: {epoch_loss:.4f} | Val Acc: {epoch_acc:.4f}")

        # 保存最佳模型
        if epoch_acc > best_acc:
            best_acc = epoch_acc
            torch.save(model.state_dict(), SAVE_PATH)

    print(f"\n训练运行完毕！最高准确率: {best_acc:.4f}")
    print(f"模型已保存至: {SAVE_PATH}")

    # 6. 全方位评估 (你的功劳点：深度模型分析)
    print("\n--- 正在生成仪表盘数据包 ---")
    model.eval()
    all_preds = []
    all_labels = []
    all_confs = []

    with torch.no_grad():
        for inputs, labels in val_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            probs = torch.softmax(outputs, dim=1)
            confs, preds = torch.max(probs, 1)

            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            all_confs.extend(confs.cpu().numpy())

    # 计算各项指标 (手动实现以减少库依赖)
    all_preds = np.array(all_preds)
    all_labels = np.array(all_labels)
    all_confs = np.array(all_confs)

    tp = np.sum((all_preds == 0) & (all_labels == 0)) # Cataract 为 0
    tn = np.sum((all_preds == 1) & (all_labels == 1)) # Normal 为 1
    fp = np.sum((all_preds == 0) & (all_labels == 1))
    fn = np.sum((all_preds == 1) & (all_labels == 0))

    acc = (tp + tn) / len(all_labels)
    prec = tp / (tp + fp) if (tp + fp) > 0 else 0
    rec = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0
    spec = tn / (tn + fp) if (tn + fp) > 0 else 0

    # 计算分类详细指标
    cat_count = np.sum(all_labels == 0)
    norm_count = np.sum(all_labels == 1)
    cat_correct = tp
    norm_correct = tn

    # 置信度分布 (6个分段: <0.5, 0.5-0.6, 0.6-0.7, 0.7-0.8, 0.8-0.9, 0.9-1.0)
    bins = [0, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    hist, _ = np.histogram(all_confs, bins=bins)

    # 打印 JSON 数据包 (你可以直接复制到 data.js 中)
    print("\n" + "="*50)
    print("📢 复制以下内容添加到 visualization/js/data.js 的 MODEL_DATA 中:")
    print("="*50)
    import json
    dashboard_data = {
        "overall": {
            "accuracy": round(float(acc), 4),
            "precision": round(float(prec), 4),
            "recall": round(float(rec), 4),
            "f1": round(float(f1), 4),
            "specificity": round(float(spec), 4),
            "confusion_matrix": {"TP": int(tp), "TN": int(tn), "FP": int(fp), "FN": int(fn)},
            "avg_confidence": round(float(np.mean(all_confs)), 4),
            "total": int(len(all_labels)),
            "confidence_distribution": hist.tolist()
        },
        "cataract": {
            "precision": round(float(prec), 4),
            "recall": round(float(rec), 4),
            "count": int(cat_count),
            "correct": int(cat_correct),
            "avg_confidence": round(float(np.mean(all_confs[all_labels == 0])), 4) if cat_count > 0 else 0
        },
        "normal": {
            "precision": round(float(tn/(tn+fn))) if (tn+fn)>0 else 0,
            "recall": round(float(tn/(tn+fp))) if (tn+fp)>0 else 0,
            "count": int(norm_count),
            "correct": int(norm_correct),
            "avg_confidence": round(float(np.mean(all_confs[all_labels == 1])), 4) if norm_count > 0 else 0
        }
    }
    print(f'  "Lead_Model": {json.dumps(dashboard_data, indent=4, ensure_ascii=False)},')
    print("="*50)

    # 7. 自动绘图
    plt.figure(figsize=(10, 4))
    plt.subplot(1, 2, 1)
    plt.plot(history['train_loss'], label='Loss')
    plt.title('Training Loss')
    plt.subplot(1, 2, 2)
    plt.plot(history['val_acc'], label='Accuracy')
    plt.title('Validation Accuracy')
    plt.savefig('training_result.png')
    print("\n训练结果分析图已生成: training_result.png")

if __name__ == "__main__":
    train_model()