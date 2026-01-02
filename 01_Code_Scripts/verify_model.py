import torch
import torch.nn as nn
from torchvision import models, transforms, datasets
from torch.utils.data import DataLoader
import numpy as np
from sklearn.metrics import confusion_matrix

# 配置
MODEL_PATH = "result/best_cataract_model.pth"
DATA_PATH = "04data/ALL_Data_split12/Test"

print("="*60)
print("重新验证 PyTorch 模型")
print("="*60)

# 加载模型
device = torch.device("cpu")
model = models.resnet18(weights=None)
model.fc = nn.Linear(model.fc.in_features, 2)
model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
model.eval()

# 准备数据
data_transforms = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

dataset = datasets.ImageFolder(DATA_PATH, transform=data_transforms)
dataloader = DataLoader(dataset, batch_size=32, shuffle=False)

print(f"\n数据集信息:")
print(f"  总数: {len(dataset)}")
print(f"  类别: {dataset.class_to_idx}")

# 评估
all_preds = []
all_labels = []

print("\n开始评估...")
with torch.no_grad():
    for inputs, labels in dataloader:
        outputs = model(inputs)
        _, preds = torch.max(outputs, 1)
        all_preds.extend(preds.cpu().numpy())
        all_labels.extend(labels.cpu().numpy())

# 计算混淆矩阵
all_labels = np.array(all_labels)
all_preds = np.array(all_preds)

cm = confusion_matrix(all_labels, all_preds)
tp = cm[0, 0]
fn = cm[0, 1]
fp = cm[1, 0]
tn = cm[1, 1]

total = np.sum(cm)
accuracy = (tp + tn) / total
precision = tp / (tp + fp) if (tp + fp) > 0 else 0
recall = tp / (tp + fn) if (tp + fn) > 0 else 0
f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

print(f"\n评估结果:")
print(f"  准确率: {accuracy:.4f} ({accuracy*100:.2f}%)")
print(f"  精确率: {precision:.4f}")
print(f"  召回率: {recall:.4f}")
print(f"  F1分数: {f1:.4f}")
print(f"\n混淆矩阵:")
print(f"  TP (正确识别白内障): {tp}")
print(f"  TN (正确识别正常): {tn}")
print(f"  FP (误判为白内障): {fp}")
print(f"  FN (漏判白内障): {fn}")
print(f"\n错误总数: {fp + fn}")

print("="*60)
