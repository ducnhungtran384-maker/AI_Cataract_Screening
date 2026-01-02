import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import models, transforms
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import cv2
import os

# ==========================================
# 杀手锏：Grad-CAM 热力图可视化脚本
# 功能：显示 AI 在看图片的哪个位置
# ==========================================

MODEL_PATH = "result/best_cataract_model.pth"
TEST_IMAGE = "04data/ALL_Data_split12/Test/Cataract/1155.jpg" # 修改为你想要分析的图片路径

class GradCAM:
    def __init__(self, model, target_layer):
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.activations = None
        
        # 注册钩子
        self.target_layer.register_forward_hook(self.save_activation)
        self.target_layer.register_full_backward_hook(self.save_gradient)

    def save_activation(self, module, input, output):
        self.activations = output

    def save_gradient(self, module, grad_input, grad_output):
        self.gradients = grad_output[0]

    def generate_heatmap(self, input_tensor, class_idx=None):
        # 前向传播
        output = self.model(input_tensor)
        if class_idx is None:
            class_idx = torch.argmax(output)
        
        # 反向传播获取梯度
        self.model.zero_grad()
        output[0, class_idx].backward()
        
        # 计算权重 (Global Average Pooling)
        weights = torch.mean(self.gradients, dim=(2, 3), keepdim=True)
        
        # 加权叠加特征图
        cam = torch.sum(weights * self.activations, dim=1).squeeze()
        
        # ReLU & 归一化
        cam = np.maximum(cam.detach().cpu().numpy(), 0)
        if cam.max() != 0:
            cam = cam / cam.max()
            
        return cam, class_idx.item()

def run_gradcam():
    # 1. 加载模型
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = models.resnet18(pretrained=False)
    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(num_ftrs, 2)
    
    if not os.path.exists(MODEL_PATH):
        print(f"错误：没找到模型文件 {MODEL_PATH}")
        return

    model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
    model.eval().to(device)

    # 2. 预处理图片
    preprocess = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    if not os.path.exists(TEST_IMAGE):
        print(f"错误：没找到测试图片 {TEST_IMAGE}")
        return
        
    img = Image.open(TEST_IMAGE).convert('RGB')
    input_tensor = preprocess(img).unsqueeze(0).to(device)

    # 3. 指定目标层 (对于 ResNet18，通常是最后一块层 layer4)
    target_layer = model.layer4[-1]
    cam_engine = GradCAM(model, target_layer)

    # 4. 生成热力图
    heatmap, pred_idx = cam_engine.generate_heatmap(input_tensor)
    
    # 5. 后处理展示
    classes = ['Cataract', 'Normal']
    print(f"模型判定结果: {classes[pred_idx]}")

    # 将 heatmap 调整到原图大小
    heatmap_resized = cv2.resize(heatmap, (img.size[0], img.size[1]))
    heatmap_colored = cv2.applyColorMap(np.uint8(255 * heatmap_resized), cv2.COLORMAP_JET)
    heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)
    
    # 叠加
    overlayed = np.float32(heatmap_colored) + np.float32(np.array(img))
    overlayed = 255 * overlayed / np.max(overlayed)
    overlayed = np.uint8(overlayed)

    # 保存并展示结果
    plt.figure(figsize=(12, 5))
    plt.subplot(1, 3, 1)
    plt.imshow(img)
    plt.title('Original Image')
    plt.axis('off')

    plt.subplot(1, 3, 2)
    plt.imshow(heatmap_resized, cmap='jet')
    plt.title('AI Focus Area')
    plt.axis('off')

    plt.subplot(1, 3, 3)
    plt.imshow(overlayed)
    plt.title(f'Diagnosis: {classes[pred_idx]}')
    plt.axis('off')

    output_name = "gradcam_result.png"
    plt.savefig(output_name)
    print(f"热力图分析完成！结果已保存至: {output_name}")
    # plt.show()

if __name__ == "__main__":
    run_gradcam()
