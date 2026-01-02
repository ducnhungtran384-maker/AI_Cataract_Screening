import torch
import torch.nn as nn
from torchvision import datasets, models, transforms
from torch.utils.data import DataLoader
import os

# 配置
# 配置
# 相对路径：只要把数据放在脚本旁边的 'dataset' 文件夹里，发给谁都能跑
# 不要写死像 "C:\Users\..." 这种路径
DATA_PATH = "../04data/ALL_Data_split12/Test"  # 临时适配当前电脑
MODEL_PATH = "best_cataract_model.pth"
BATCH_SIZE = 1

def find_mismatches():
    # 1. 设备选择
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print(f"使用设备: {device}")

    # 2. 数据处理
    data_transforms = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    if not os.path.exists(DATA_PATH):
        print(f"错误: 找不到路径 {DATA_PATH}")
        return

    dataset = datasets.ImageFolder(DATA_PATH, transform=data_transforms)
    dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=False)

    # 3. 加载模型
    model = models.resnet18(weights=None)
    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(num_ftrs, 2)
    
    try:
        model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
        print("模型加载成功！")
    except Exception as e:
        print(f"模型加载失败: {e}")
        return
        
    model = model.to(device)
    model.eval()

    # 4. 查找不匹配
    mismatches = []
    class_names = dataset.classes # ['Cataract', 'Normal']
    
    print("\n正在扫描数据以查找不匹配项...")
    
    with torch.no_grad():
        for i, (inputs, labels) in enumerate(dataloader):
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)
            
            if preds != labels:
                img_path, _ = dataset.samples[i]
                mismatches.append({
                    'path': img_path,
                    'actual': class_names[labels.item()],
                    'predicted': class_names[preds.item()]
                })

    # 5. 输出结果
    print(f"\n找到 {len(mismatches)} 个不匹配项:")
    for m in mismatches:
        print(f"图片: {m['path']}")
        print(f"  - 人类标注: {m['actual']}")
        print(f"  - AI 预测: {m['predicted']}")
        print("-" * 20)

if __name__ == "__main__":
    find_mismatches()
