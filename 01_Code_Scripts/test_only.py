# 纯测试脚本：只输出结果，不修改任何文件
import torch
import torch.nn as nn
from torchvision import datasets, models, transforms
from torch.utils.data import DataLoader
import numpy as np
from sklearn.metrics import confusion_matrix

# ================= 配置区 =================
MODEL_PATH = "../result/best_cataract_model.pth"
DATA_PATH = "../04data/ALL_Data_split12/Test"
# ==========================================

def test_model():
    print("=" * 60)
    print("🔬 PyTorch 模型测试 (仅输出结果，不修改任何文件)")
    print("=" * 60)
    
    # 设备
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print(f"设备: {device}")
    
    # 数据预处理
    data_transforms = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    
    # 加载数据集
    dataset = datasets.ImageFolder(DATA_PATH, transform=data_transforms)
    dataloader = DataLoader(dataset, batch_size=32, shuffle=False)
    print(f"测试集路径: {DATA_PATH}")
    print(f"测试集大小: {len(dataset)} 张图片")
    print(f"类别映射: {dataset.class_to_idx}")
    
    # 加载模型 (ResNet18)
    print("\n正在加载模型...")
    model = models.resnet18(weights=None)
    model.fc = nn.Linear(model.fc.in_features, 2)
    model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
    model = model.to(device)
    model.eval()
    print("✅ 模型加载成功!")
    
    # 推理
    print("\n正在进行推理...")
    all_preds = []
    all_labels = []
    all_confs = []
    
    with torch.no_grad():
        for inputs, labels in dataloader:
            inputs = inputs.to(device)
            outputs = model(inputs)
            probs = torch.softmax(outputs, dim=1)
            confs, preds = torch.max(probs, 1)
            
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            all_confs.extend(confs.cpu().numpy())
    
    # 转为 numpy
    all_preds = np.array(all_preds)
    all_labels = np.array(all_labels)
    all_confs = np.array(all_confs)
    
    # 计算混淆矩阵
    # class 0: Cataract, class 1: Normal (ImageFolder 按字母序)
    cm = confusion_matrix(all_labels, all_preds)
    tp = cm[0, 0]  # Cataract 预测为 Cataract
    fn = cm[0, 1]  # Cataract 预测为 Normal (漏诊)
    fp = cm[1, 0]  # Normal 预测为 Cataract (误诊)
    tn = cm[1, 1]  # Normal 预测为 Normal
    
    # 计算指标
    total = len(all_labels)
    accuracy = (tp + tn) / total
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0  # 敏感度
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    
    # 输出结果
    print("\n" + "=" * 60)
    print("📊 测试结果")
    print("=" * 60)
    
    print(f"\n【混淆矩阵】")
    print(f"              预测Cataract  预测Normal")
    print(f"实际Cataract     {tp:5d}        {fn:5d}")
    print(f"实际Normal       {fp:5d}        {tn:5d}")
    
    print(f"\n【关键指标】")
    print(f"  准确率 (Accuracy):    {accuracy:.2%} ({tp+tn}/{total})")
    print(f"  精确率 (Precision):   {precision:.2%}")
    print(f"  召回率 (Recall):      {recall:.2%} (敏感度/漏诊率的对立面)")
    print(f"  特异度 (Specificity): {specificity:.2%} (误诊率的对立面)")
    print(f"  F1 Score:             {f1:.4f}")
    print(f"  平均置信度:           {np.mean(all_confs):.2%}")
    
    print(f"\n【分类详情】")
    cataract_count = np.sum(all_labels == 0)
    normal_count = np.sum(all_labels == 1)
    print(f"  Cataract: {tp}/{cataract_count} 正确 ({tp/cataract_count:.2%})")
    print(f"  Normal:   {tn}/{normal_count} 正确 ({tn/normal_count:.2%})")
    
    print(f"\n【置信度分布】")
    bins = [0, 0.6, 0.7, 0.8, 0.9, 0.95, 1.0]
    hist, _ = np.histogram(all_confs, bins=bins)
    print(f"  <60%:     {hist[0]}")
    print(f"  60%-70%:  {hist[1]}")
    print(f"  70%-80%:  {hist[2]}")
    print(f"  80%-90%:  {hist[3]}")
    print(f"  90%-95%:  {hist[4]}")
    print(f"  >95%:     {hist[5]}")
    
    # JSON 格式输出 (方便后续使用)
    print(f"\n【JSON 格式 (供后续集成用)】")
    import json
    result = {
        "overall": {
            "accuracy": round(accuracy, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "specificity": round(specificity, 4),
            "confusion_matrix": {"TP": int(tp), "TN": int(tn), "FP": int(fp), "FN": int(fn)},
            "avg_confidence": round(float(np.mean(all_confs)), 4),
            "total": int(total),
            "confidence_distribution": hist.tolist()
        },
        "cataract": {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "count": int(cataract_count),
            "correct": int(tp),
            "avg_confidence": round(float(np.mean(all_confs[all_labels == 0])), 4)
        },
        "normal": {
            "precision": round(tn/(tn+fn) if (tn+fn)>0 else 0, 4),
            "recall": round(specificity, 4),
            "count": int(normal_count),
            "correct": int(tn),
            "avg_confidence": round(float(np.mean(all_confs[all_labels == 1])), 4)
        }
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 60)
    print("✅ 测试完成! 以上数据未写入任何文件")
    print("=" * 60)

if __name__ == "__main__":
    test_model()
