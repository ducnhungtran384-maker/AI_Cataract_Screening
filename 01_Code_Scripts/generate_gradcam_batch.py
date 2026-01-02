import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import numpy as np
import matplotlib
matplotlib.use('Agg')  # 非交互式后端
import matplotlib.pyplot as plt
import cv2
import os
import json
import re
from tqdm import tqdm

# ==========================================
# Grad-CAM 批量生成脚本
# 为所有错误案例生成热力图
# ==========================================

# 配置
MODEL_PATH = "../result/best_cataract_model.pth"
ERROR_DATA_JS = "../visualization/js/error_data.js"
ERROR_IMAGES_DIR = "../visualization/error_images"
OUTPUT_DIR = "../visualization/gradcam_heatmaps"

class GradCAM:
    def __init__(self, model, target_layer):
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.activations = None
        
        self.target_layer.register_forward_hook(self.save_activation)
        self.target_layer.register_full_backward_hook(self.save_gradient)

    def save_activation(self, module, input, output):
        self.activations = output

    def save_gradient(self, module, grad_input, grad_output):
        self.gradients = grad_output[0]

    def generate_heatmap(self, input_tensor, class_idx=None):
        output = self.model(input_tensor)
        if class_idx is None:
            class_idx = torch.argmax(output)
        
        self.model.zero_grad()
        output[0, class_idx].backward()
        
        weights = torch.mean(self.gradients, dim=(2, 3), keepdim=True)
        cam = torch.sum(weights * self.activations, dim=1).squeeze()
        
        cam = np.maximum(cam.detach().cpu().numpy(), 0)
        if cam.max() != 0:
            cam = cam / cam.max()
            
        return cam, class_idx.item()

def parse_error_cases(error_data_js):
    """从 error_data.js 中解析错误案例"""
    with open(error_data_js, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取 filename
    filenames = re.findall(r'"filename":\s*"([^"]+)"', content)
    return filenames

def generate_gradcam_batch():
    print("="*60)
    print("Grad-CAM 批量生成脚本")
    print("="*60)
    
    # 1. 创建输出目录
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"✅ 创建输出目录: {OUTPUT_DIR}")
    
    # 2. 加载模型
    print("\n📦 加载模型...")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = models.resnet18(weights=None)
    model.fc = nn.Linear(model.fc.in_features, 2)
    
    try:
        model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
        model = model.to(device).eval()
        print(f"✅ 模型加载成功 (设备: {device})")
    except Exception as e:
        print(f"❌ 模型加载失败: {e}")
        return
    
    # 3. 解析错误案例
    print("\n📋 解析错误案例列表...")
    error_files = parse_error_cases(ERROR_DATA_JS)
    print(f"✅ 找到 {len(error_files)} 个错误案例")
    
    # 4. 准备 Grad-CAM
    target_layer = model.layer4[-1]
    cam_engine = GradCAM(model, target_layer)
    
    # 5. 预处理
    preprocess = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    
    # 6. 批量生成
    print("\n🔥 开始生成 Grad-CAM 热力图...\n")
    successful = []
    failed = []
    
    for filename in tqdm(error_files, desc="生成进度"):
        try:
            # 读取图片
            img_path = os.path.join(ERROR_IMAGES_DIR, filename)
            if not os.path.exists(img_path):
                failed.append((filename, "文件不存在"))
                continue
            
            img = Image.open(img_path).convert('RGB')
            input_tensor = preprocess(img).unsqueeze(0).to(device)
            
            # 生成热力图
            heatmap, pred_idx = cam_engine.generate_heatmap(input_tensor)
            
            # 调整大小并上色
            heatmap_resized = cv2.resize(heatmap, (img.size[0], img.size[1]))
            heatmap_colored = cv2.applyColorMap(np.uint8(255 * heatmap_resized), cv2.COLORMAP_JET)
            heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)
            
            # 叠加
            overlayed = np.float32(heatmap_colored) * 0.4 + np.float32(np.array(img)) * 0.6
            overlayed = np.uint8(overlayed)
            
            # 创建三图对比
            fig, axes = plt.subplots(1, 3, figsize=(15, 5))
            
            axes[0].imshow(img)
            axes[0].set_title('Original Image', fontsize=12)
            axes[0].axis('off')
            
            axes[1].imshow(heatmap_resized, cmap='jet')
            axes[1].set_title('AI Focus Heatmap', fontsize=12)
            axes[1].axis('off')
            
            axes[2].imshow(overlayed)
            classes = ['Cataract', 'Normal']
            axes[2].set_title(f'Prediction: {classes[pred_idx]}', fontsize=12)
            axes[2].axis('off')
            
            plt.tight_layout()
            
            # 保存
            output_filename = os.path.splitext(filename)[0] + '_gradcam.png'
            output_path = os.path.join(OUTPUT_DIR, output_filename)
            plt.savefig(output_path, dpi=100, bbox_inches='tight')
            plt.close()
            
            successful.append(filename)
            
        except Exception as e:
            failed.append((filename, str(e)))
    
    # 7. 统计报告
    print("\n" + "="*60)
    print("📊 生成完成统计")
    print("="*60)
    print(f"✅ 成功: {len(successful)} 张")
    print(f"❌ 失败: {len(failed)} 张")
    
    if failed:
        print("\n失败列表:")
        for fname, reason in failed:
            print(f"  - {fname}: {reason}")
    
    print(f"\n💾 热力图已保存至: {OUTPUT_DIR}")
    print("="*60)
    
    return successful, failed

if __name__ == "__main__":
    generate_gradcam_batch()
