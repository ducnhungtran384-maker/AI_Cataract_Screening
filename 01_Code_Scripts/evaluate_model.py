import torch
import torch.nn as nn
from torchvision import datasets, models, transforms
from torch.utils.data import DataLoader
import os
import shutil
import json
import numpy as np
from sklearn.metrics import confusion_matrix
import hashlib

# ================= 配置区 =================
# 1. 模型路径 (绝对路径或相对路径)
MODEL_PATH = "../result/best_cataract_model.pth"

# 2. 数据集路径 (用户确认的测试集位置)
DATA_PATH = "../04data/ALL_Data_split12/Test"

# 3. 错误图片输出目录 (对接大屏生成器)
ERROR_IMG_DIR = "../visualization/error_images"

# 4. JSON 数据输出位置 (我们要去修改这个文件)
JS_DATA_FILE = "../visualization/js/data.js"
NEW_MODEL_NAME = "PyTorch_ResNet"
# ==========================================

def get_file_hash(file_path):
    """计算文件MD5，防重复"""
    with open(file_path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def evaluate_and_export():
    print("🚀 Starting model evaluation...")
    
    # --- 1. Device setup ---
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print(f"   Device: {device}")
    
    # Ensure error image directory exists
    if not os.path.exists(ERROR_IMG_DIR):
        os.makedirs(ERROR_IMG_DIR)
        print(f"   Created directory: {ERROR_IMG_DIR}")

    # --- 2. Prepare data ---
    if not os.path.exists(DATA_PATH):
        print(f"❌ Error: Dataset path not found: {DATA_PATH}")
        return

    data_transforms = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    
    dataset = datasets.ImageFolder(DATA_PATH, transform=data_transforms)
    dataloader = DataLoader(dataset, batch_size=32, shuffle=False) # Batch inference is faster
    print(f"   Dataset: {len(dataset)} images")
    print(f"   Classes: {dataset.class_to_idx}")

    # --- 3. Load model ---
    print("   Loading model...")
    model = models.resnet18(weights=None)
    # 必须先修改 fc 层架构以匹配保存的模型（2分类而非1000分类）
    # load_state_dict 会用保存的权重覆盖这里的随机初始化
    model.fc = nn.Linear(model.fc.in_features, 2)
    try:
        model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
        model = model.to(device)
        model.eval()  # 设置为评估模式
        print("Model loaded successfully!")
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        return

    # --- 4. Batch inference ---
    all_preds = []
    all_labels = []
    all_probs = [] # Store confidence scores
    mismatches = []
    
    cat_probs = []
    norm_probs = []
    
    print("   Running inference...")
    with torch.no_grad():
        for i, (inputs, labels) in enumerate(dataloader):
            inputs = inputs.to(device)
            outputs = model(inputs)
            
            # 计算概率 (Softmax)
            probs = torch.nn.functional.softmax(outputs, dim=1)
            confidence, preds = torch.max(probs, 1)
            
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            all_probs.extend(confidence.cpu().numpy())

            # 分类收集置信度
            for k in range(len(labels)):
                label_idx = labels[k].item()
                conf_val = confidence[k].item()
                
                if label_idx == dataset.class_to_idx['Cataract']: 
                    cat_probs.append(conf_val)
                else:
                    norm_probs.append(conf_val)
            # 记录错误样本
            batch_start_idx = i * dataloader.batch_size
            for k in range(len(preds)):
                if preds[k] != labels[k]:
                    global_idx = batch_start_idx + k
                    img_path, _ = dataset.samples[global_idx]
                    mismatches.append({
                        'path': img_path,
                        'actual': labels[k].item(),
                        'predicted': preds[k].item(),
                        'confidence': confidence[k].item()
                    })

    # --- 5. 计算医学指标 ---
    # 混淆矩阵: tn, fp, fn, tp (注意 sklearn 的顺序)
    # class 0: Cataract (Positive?), class 1: Normal (Negative?)
    # 通常 ImageFolder 是按字母排序: Cataract (0), Normal (1)
    # 假设 0:Cataract 是阳性, 1:Normal 是阴性
    # 混淆矩阵 [[TP, FN], [FP, TN]] 取决于标签定义
    # 让我们明确定义: Target=0(Cataract) is Positive. 
    
    all_labels = np.array(all_labels)
    all_preds = np.array(all_preds)
    
    # SKLearn confusion matrix
    cm = confusion_matrix(all_labels, all_preds) 
    # Label 0 (Cataract), Label 1 (Normal)
    # [ [True 0, False 1], 
    #   [False 0, True 1] ]
    # 即: [[TP, FN], [FP, TN]] (如果 0 是 Positive)
    
    tp = cm[0, 0] # 真实是0，预测是0
    fn = cm[0, 1] # 真实是0，预测是1 (漏诊)
    fp = cm[1, 0] # 真实是1，预测是0 (误诊)
    tn = cm[1, 1] # 真实是1，预测是1
    
    total = np.sum(cm)
    accuracy = (tp + tn) / total
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0 # 敏感度 Sensitivity
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0 # 特异度
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    # 6. 处理错误图片 (复制并去重)
    print(f"   Found {len(mismatches)} error samples, processing images...")
    if not os.path.exists(ERROR_IMG_DIR):
         os.makedirs(ERROR_IMG_DIR)

    saved_error_images = []
    
    for m in mismatches:
        src_path = m['path']
        filename = os.path.basename(src_path)
        
        # 添加类别前缀以避免同名冲突（Normal/3660.jpg vs Cataract/3660.jpg）
        # 从路径中提取真实类别
        parent_dir = os.path.basename(os.path.dirname(src_path))
        prefixed_filename = f"{parent_dir.lower()}_{filename}"
        
        dst_path = os.path.join(ERROR_IMG_DIR, prefixed_filename)
        shutil.copy2(src_path, dst_path)
        saved_error_images.append(prefixed_filename)

    # 7. 构建 JSON 结构
    # 置信度分布 (Histogram, 6 bins like 0.5-0.6, ..., 0.9-1.0)
    # 原始可视为 [0, 6, 7, 4, 15, 602] 这种计数
    # 我们简单将置信度分桶
    conf_bins = [0] * 6 # <0.6, 0.6-0.7, 0.7-0.8, 0.8-0.9, 0.9-0.95, >0.95
    for p in all_probs:
        if p < 0.6: conf_bins[0] += 1
        elif p < 0.7: conf_bins[1] += 1
        elif p < 0.8: conf_bins[2] += 1
        elif p < 0.9: conf_bins[3] += 1
        elif p < 0.95: conf_bins[4] += 1
        else: conf_bins[5] += 1

    model_json = {
        "overall": {
            "accuracy": round(accuracy, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "specificity": round(specificity, 4),
            "confusion_matrix": {
                "TP": int(tp), "TN": int(tn), "FP": int(fp), "FN": int(fn)
            },
            "avg_confidence": round(float(np.mean(all_probs)), 4),
            "total": int(total),
            "confidence_distribution": conf_bins
        },
        "cataract": {
            "precision": round(tp / (tp+fp) if (tp+fp)>0 else 0, 4),
            "recall": round(tp / (tp+fn) if (tp+fn)>0 else 0, 4),
            "accuracy": round(tp / (tp+fn) if (tp+fn)>0 else 0, 4), # Class accuracy = Recall (TP/Actual Positives)
            "f1": round(2 * (tp / (tp+fp)) * (tp / (tp+fn)) / ((tp / (tp+fp)) + (tp / (tp+fn))) if ((tp / (tp+fp)) + (tp / (tp+fn))) > 0 else 0, 4),
            "count": int(tp+fn),
            "correct": int(tp),
            "avg_confidence": round(float(np.mean(cat_probs)) if cat_probs else 0, 4)
        },
        "normal": {
            "precision": round(tn / (tn+fn) if (tn+fn)>0 else 0, 4),
            "recall": round(tn / (tn+fp) if (tn+fp)>0 else 0, 4),
            "accuracy": round(tn / (tn+fp) if (tn+fp)>0 else 0, 4), # Class accuracy = Recall (TN/Actual Negatives)
            "f1": round(2 * (tn / (tn+fn)) * (tn / (tn+fp)) / ((tn / (tn+fn)) + (tn / (tn+fp))) if ((tn / (tn+fn)) + (tn / (tn+fp))) > 0 else 0, 4),
            "count": int(tn+fp),
            "correct": int(tn),
            "avg_confidence": round(float(np.mean(norm_probs)) if norm_probs else 0, 4)
        }
    }
    
    print("\n✅ Metrics calculation complete:")
    print(f"   Accuracy: {accuracy:.2%}")
    print(f"   F1 Score: {f1:.4f}")
    
    # 8. 导出错误案例到 error_data.js
    export_error_cases(mismatches, dataset.class_to_idx)
    
    # 9. 注入到 data.js
    # 这是一个比较暴力的文本替换，但最有效
    inject_to_js(model_json)

def export_error_cases(mismatches, class_to_idx):
    """导出错误案例到 error_data.js"""
    print(f"\n📊 Exporting {len(mismatches)} error cases to error_data.js...")
    
    # 反转 class_to_idx 以便从索引获取类名
    idx_to_class = {v: k for k, v in class_to_idx.items()}
    
    # 构建错误案例列表
    error_cases = []
    for m in mismatches:
        filename = os.path.basename(m['path'])
        
        # 添加类别前缀
        parent_dir = os.path.basename(os.path.dirname(m['path']))
        prefixed_filename = f"{parent_dir.lower()}_{filename}"
        
        error_cases.append({
            "filename": prefixed_filename,
            "true_label": idx_to_class[m['actual']],
            "pred_label": idx_to_class[m['predicted']],
            "confidence": round(m['confidence'], 8),
            "image_path": f"error_images/{prefixed_filename}"
        })
    
    # 生成 JavaScript 代码
    js_content = "const ERROR_CASES = [\n"
    for i, case in enumerate(error_cases):
        js_content += "  {\n"
        js_content += f'    "filename": "{case["filename"]}",\n'
        js_content += f'    "true_label": "{case["true_label"]}",\n'
        js_content += f'    "pred_label": "{case["pred_label"]}",\n'
        js_content += f'    "confidence": {case["confidence"]},\n'
        js_content += f'    "image_path": "{case["image_path"]}"\n'
        js_content += "  }"
        if i < len(error_cases) - 1:
            js_content += ","
        js_content += "\n"
    js_content += "];\n"
    
    # 写入文件
    error_data_path = "../visualization/js/error_data.js"
    with open(error_data_path, 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    print(f"✅ Exported {len(error_cases)} error cases to {error_data_path}")
    return error_cases

def inject_to_js(json_data):
    print("\n✍️ Injecting data into data.js...")
    
    with open(JS_DATA_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # 将 JSON 对象转为字符串，但要去掉最外层的花括号，以便塞进去
    # 或者我们直接找 const MODEL_DATA = { 后面的位置插入
    
    json_str = json.dumps(json_data, indent=4, ensure_ascii=False)
    # 我们构造一个 key: value 字符串，注意缩进
    # key 不需要引号? JS里还是需要的最好
    insertion = f'  "{NEW_MODEL_NAME}": {json_str},\n'
    
    # 寻找插入点：MODEL_DATA = { 之后
    marker = "const MODEL_DATA = {"
    pos = content.find(marker)
    if pos == -1:
        print("❌ Cannot find insertion point in data.js")
        return
        
    # 插入
    new_content = content[:pos + len(marker)] + "\n" + insertion + content[pos + len(marker):]
    
    # 还需要更新 MODEL_NAMES 列表
    # 找到 const MODEL_NAMES = [
    marker_names = "const MODEL_NAMES = ["
    pos_names = new_content.find(marker_names)
    if pos_names != -1:
        # 在 [ 后面插入 "PyTorch_ResNet", 
        new_content = new_content[:pos_names + len(marker_names)] + f'"{NEW_MODEL_NAME}", ' + new_content[pos_names + len(marker_names):]
    
    # 写入
    with open(JS_DATA_FILE, 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    print("✅ Data injection successful!")

if __name__ == "__main__":
    evaluate_and_export()
