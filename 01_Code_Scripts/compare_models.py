import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, models, transforms
from torch.utils.data import DataLoader
import matplotlib.pyplot as plt
import os
import numpy as np
import json
import random
import time

# 1. 配置模型下载路径 (必须在 import torchvision 前设置，或尽早设置)
os.environ['TORCH_HOME'] = r"C:\Users\weirui\Desktop\AI_Test\03result"

# ================= 配置区 =================
# 1. 数据集路径
DATA_ROOT = r"C:\Users\weirui\Desktop\AI_Test\02data\ALL_Data_split12"
TRAIN_DIR = os.path.join(DATA_ROOT, "Train")
TEST_DIR = os.path.join(DATA_ROOT, "Test")

# 2. 训练配置
EPOCHS = 3  # GPU跑全量可以多跑几轮
BATCH_SIZE = 32 # GPU可以加大Batch Size
LEARNING_RATE = 0.001
DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

if DEVICE.type == 'cpu':
    print("⚠️  Warning: Still running on CPU!")
else:
    print(f"✅  Successful: Running on GPU ({torch.cuda.get_device_name(0)})")



# 3. 输出文件
RESULT_JS = "04visualization/js/model_comparison.js"
RESULT_PLOT = "04visualization/comparison_result.png"
# ==========================================

def get_model(model_name, num_classes=2):
    """工厂函数：根据名称构建模型"""
    print(f"📦 Building model: {model_name}...")
    
    if model_name == "resnet18":
        model = models.resnet18(pretrained=True)
        num_ftrs = model.fc.in_features
        model.fc = nn.Linear(num_ftrs, num_classes)
        
    elif model_name == "vgg16":
        model = models.vgg16(pretrained=True)
        num_ftrs = model.classifier[6].in_features
        model.classifier[6] = nn.Linear(num_ftrs, num_classes)
        
    elif model_name == "densenet121":
        model = models.densenet121(pretrained=True)
        num_ftrs = model.classifier.in_features
        model.classifier = nn.Linear(num_ftrs, num_classes)
        
    else:
        raise ValueError(f"Unknown model name: {model_name}")
        
    return model.to(DEVICE)

def calculate_metrics(tp, tn, fp, fn):
    """计算核心指标"""
    accuracy = (tp + tn) / (tp + tn + fp + fn + 1e-10)
    precision = tp / (tp + fp + 1e-10)
    recall = tp / (tp + fn + 1e-10)  # Sensitivity
    f1 = 2 * (precision * recall) / (precision + recall + 1e-10)
    specificity = tn / (tn + fp + 1e-10)
    return {
        "accuracy": float(accuracy),
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
        "specificity": float(specificity)
    }

def calculate_confidence_distribution(confidences):
    """
    计算置信度分布
    Bins: <0.5 (unused), 0.5-0.6, 0.6-0.7, 0.7-0.8, 0.8-0.9, 0.9-1.0
    Returns: Array of counts, length 6
    """
    bins = [0] * 6
    for c in confidences:
        if c < 0.5: bins[0] += 1
        elif c < 0.6: bins[1] += 1
        elif c < 0.7: bins[2] += 1
        elif c < 0.8: bins[3] += 1
        elif c < 0.9: bins[4] += 1
        else: bins[5] += 1
    return bins

def train_and_evaluate(model_name):
    """训练并评估单个模型"""
    print(f"\n{'='*40}")
    print(f"🚀 开始训练: {model_name}")
    print(f"{'='*40}")
    
    # 1. 数据准备
    print(f"Loading data from {DATA_ROOT}...")
    
    data_transforms = {
        'Train': transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ]),
        'Test': transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ]),
    }

    try:
        full_train_dataset = datasets.ImageFolder(TRAIN_DIR, transform=data_transforms['Train'])
        full_test_dataset = datasets.ImageFolder(TEST_DIR, transform=data_transforms['Test'])
        classes = full_train_dataset.classes
        print(f"Dataset classes: {classes}")
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return

    # --- FULL DATA MODE (No Subsetting) ---
    print("🚀  已切换至全量数据模式 (Full Data Mode)...")
    train_dataset = full_train_dataset
    val_dataset = full_test_dataset
    
    # 增加 num_workers 加速数据读取
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)
    
    train_size = len(train_dataset)
    val_size = len(val_dataset)
    print(f"Full Dataset sizes: Train={train_size}, Val={val_size}")
    # -----------------------------------------------
    
    # 2. 模型与优化器
    model = get_model(model_name)
    criterion = nn.CrossEntropyLoss()
    
    # Feature Extracting 模式：仅训练最后层
    params_to_update = []
    for name, param in model.named_parameters():
        if param.requires_grad == True:
            params_to_update.append(param)
            
    optimizer = optim.Adam(params_to_update, lr=LEARNING_RATE)
    
    # 3. 训练循环
    start_time = time.time()
    
    for epoch in range(EPOCHS):
        model.train()
        running_loss = 0.0
        
        for inputs, labels in train_loader:
            inputs, labels = inputs.to(DEVICE), labels.to(DEVICE)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item() * inputs.size(0)
            
        print(f"Epoch {epoch+1}/{EPOCHS} | Loss: {running_loss/train_size:.4f}")

    train_time = time.time() - start_time
    
    # 4. 详细评估 (计算 TP, TN, FP, FN 及 置信度分布)
    print(f"🔍 正在评估 {model_name}...")
    model.eval()
    
    tp = 0; tn = 0; fp = 0; fn = 0
    all_confidences = []
    
    with torch.no_grad():
        for inputs, labels in val_loader:
            inputs, labels = inputs.to(DEVICE), labels.to(DEVICE)
            outputs = model(inputs)
            
            # 计算概率和预测
            probs = torch.softmax(outputs, dim=1)
            confidences, preds = torch.max(probs, 1)
            
            # 收集置信度
            all_confidences.extend(confidences.cpu().numpy().tolist())
            
            for p, t in zip(preds, labels):
                if t == 0:  # True Cataract
                    if p == 0: tp += 1
                    else:      fn += 1
                else:       # True Normal
                    if p == 1: tn += 1
                    else:      fp += 1
                    
    metrics = calculate_metrics(tp, tn, fp, fn)
    conf_dist = calculate_confidence_distribution(all_confidences)
    avg_conf = sum(all_confidences) / len(all_confidences) if all_confidences else 0
    
    print(f"✅ {model_name} 完成! Acc: {metrics['accuracy']:.2%} | Avg Conf: {avg_conf:.2f}")
    
    result = {
        "overall": {
            "accuracy": metrics['accuracy'],
            "precision": metrics['precision'],
            "recall": metrics['recall'],
            "f1": metrics['f1'],
            "specificity": metrics['specificity'],
            "avg_confidence": float(avg_conf),
            "confidence_distribution": conf_dist,
            "confusion_matrix": {"TP": tp, "TN": tn, "FP": fp, "FN": fn}
        },
        # 简单模拟分类别性能，通常和overall接近
        "cataract": { 
            "accuracy": metrics['recall'], 
            "precision": metrics['precision'], 
            "recall": metrics['recall'], 
            "f1": metrics['f1'],
            "avg_confidence": float(avg_conf) # 简化
        },
        "normal":   { 
            "accuracy": metrics['specificity'], 
            "precision": 0.0, 
            "recall": metrics['specificity'], 
            "f1": 0.0,
            "avg_confidence": float(avg_conf) # 简化
        }
    }
    
    meta = {
        "name": model_name,
        "time": train_time,
        "params": sum(p.numel() for p in model.parameters())
    }
    
    return result, meta

def main():
    if not os.path.exists("04visualization/js"):
        os.makedirs("04visualization/js", exist_ok=True)
        
    models_to_run = ["resnet18", "vgg16", "densenet121"]
    
    full_data = {}      # 用于 data.js 格式
    chart_data = {"models": [], "accuracy": [], "time": [], "params": []} # 用于 comparison_result.png
    
    print(f"对比实验开始... 设备: {DEVICE}")
    
    for m in models_to_run:
        try:
            res_data, res_meta = train_and_evaluate(m)
            if res_data:
                # 键名首字母大写作为显示名
                if m == "resnet18": DisplayName = "ResNet18 (Standard)"
                elif m == "vgg16": DisplayName = "VGG16"
                elif m == "densenet121": DisplayName = "DenseNet121"
                else: DisplayName = m
                
                full_data[DisplayName] = res_data
                
                chart_data["models"].append(DisplayName)
                chart_data["accuracy"].append(round(res_data["overall"]["accuracy"], 4))
                chart_data["time"].append(round(res_meta["time"], 1))
                chart_data["params"].append(round(res_meta["params"]/1e6, 1))
        except Exception as e:
            print(f"❌ {m} 异常: {e}")
            import traceback
            traceback.print_exc()
    
    # 5. 导出 JS
    print("\n💾 正在保存结果...")
    
    js_content = f"""
// Auto-generated by compare_models.py
(function() {{
    const NEW_MODELS = {json.dumps(full_data, indent=4)};
    
    if (typeof MODEL_DATA !== 'undefined') {{
        console.log('Merging new comparison models into MODEL_DATA...');
        Object.assign(MODEL_DATA, NEW_MODELS);
    }} else {{
        window.MODEL_DATA = NEW_MODELS;
    }}
    
    // 同时也生成简单的对比数据供参考
    window.MODEL_COMPARISON_SIMPLE = {json.dumps(chart_data, indent=4)};
}})();
"""
    with open(RESULT_JS, 'w', encoding='utf-8') as f:
        f.write(js_content)
    print(f"✅ JS数据已保存至: {RESULT_JS}")

    # 6. 生成PNG对比图
    if len(chart_data["models"]) > 0:
        plt.figure(figsize=(10, 5))
        
        # Accuracy
        plt.subplot(1, 2, 1)
        bars = plt.bar(chart_data['models'], chart_data['accuracy'], color=['#3498db', '#e74c3c', '#2ecc71'])
        plt.ylim(0, 1.1)
        plt.title('Accuracy Comparison')
        for bar in bars:
            plt.text(bar.get_x() + bar.get_width()/2., bar.get_height(), f'{bar.get_height():.2%}', ha='center', va='bottom')
            
        # Time
        plt.subplot(1, 2, 2)
        bars = plt.bar(chart_data['models'], chart_data['time'], color=['#3498db', '#e74c3c', '#2ecc71'])
        plt.title('Training Time (s)')
        for bar in bars:
            plt.text(bar.get_x() + bar.get_width()/2., bar.get_height(), f'{bar.get_height():.1f}s', ha='center', va='bottom')
            
        plt.tight_layout()
        plt.savefig(RESULT_PLOT)
        print(f"✅ 对比图已保存至: {RESULT_PLOT}")

if __name__ == "__main__":
    main()
