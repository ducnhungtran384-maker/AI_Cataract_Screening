# 👁️ AI 辅助白内障筛查系统 (AI-Assisted Cataract Screening System)

> 基于 PyTorch ResNet18 与 Web 可视化看板的眼科医疗辅助诊断平台

![Project Status](https://img.shields.io/badge/Status-Completed-success)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![PyTorch](https://img.shields.io/badge/PyTorch-2.0-ee4c2c)
![ECharts](https://img.shields.io/badge/Visualization-ECharts%205.0-green)

## 📖 项目背景 (Background)

白内障是全球致盲的首要原因。在医疗资源匮乏的地区，缺乏专业的眼科医生和设备导致大量患者无法及时确诊。本课题旨在开发一套**低成本、高精度、可解释**的 AI 辅助筛查系统，通过深度学习技术对眼底图像进行自动分类，并提供“红绿灯”式的直观诊断建议，赋能基层医疗。

## 🚀 核心功能 (Key Features)

*   **高精度诊断**: 基于 **ResNet18** 深度残差网络，在独立测试集上达到 **95.68%** 的准确率。
*   **全流程数据工程**: 包含自动化标签清洗 (`classify.py`)、二进制去重 (`remove_duplicate.py`) 和动态数据增强。
*   **可解释性分析 (XAI)**: 集成 **Grad-CAM** 热力图，直观展示模型关注的病灶区域（如晶状体混浊），解决“黑盒”信任问题。
*   **交互式可视化看板**: 基于 HTML5 + ECharts 构建的 Web 仪表盘，支持 3D 性能对比、雷达图评估及误判案例交互分析。

## 🛠️ 技术栈 (Tech Stack)

### 🧠 深度学习 (Deep Learning)
*   **Framework**: PyTorch 2.0 (CUDA 11.8 Accelerated)
*   **Models**: ResNet18 (Main), VGG16, DenseNet121 (Comparison), MobileNet (Baseline)
*   **Techniques**: Transfer Learning (ImageNet), Dynamic Data Augmentation, CrossEntropyLoss (Weighted)

### 📊 数据工程 & 后端 (Data & Backend)
*   **Python Libraries**: Pandas, Numpy, OpenCV, Scikit-learn
*   **Tools**: Regex (Data Injection), Hashlib (Deduplication)

### 💻 前端可视化 (Frontend Visualization)
*   **Core**: HTML5, CSS3 (Flexbox), JavaScript (ES6)
*   **Libraries**: Apache ECharts 5.4, ECharts-GL 2.0 (3D Charts), FontAwesome 6.4

## 📂 目录结构说明 (Project Structure)

本项目包含四个核心模块：

```
AI_Cataract_Screening/
├── 01_Code_Scripts/       # 🔧 核心代码库
│   ├── train_model.py         # 模型训练脚本
│   ├── classify.py            # 数据清洗与分拣
│   ├── generate_gradcam.py    # 热力图生成
│   ├── patch_data_js.py       # 数据自动注入前端脚本
│   └── ...
│
├── 02data/                # 💾 数据集 (GitIgnore - Download Separately)
│   ├── origin/                # 原始数 (Kaggle/OpenI)
│   └── sorted_data/           # 清洗后的标准数据集
│
├── 03result/              # 📈 训练输出
│   ├── best_model.pth         # 训练好的模型权重
│   ├── logs/                  # 训练日志
│   └── gradcam_heatmaps/      # 生成的热力图结果
│
├── 04visualization/       # 🌐 Web 可视化看板 (直接运行 index.html)
│   ├── index.html             # 看板入口文件
│   ├── js/data.js             # 模型性能数据 (自动注入)
│   └── js/charts.js           # 图表渲染逻辑
│
├── AI辅助白内障筛查实践报告_完美终稿.docx  # 📄 完整的项目实践报告
└── visualization_package.zip               # 📦 完整打包的可视化系统
```

## 📊 实验结果 (Results)

经过多次实验对比，我们的最终模型 (PyTorch ResNet18) 在性能与效率上取得了最佳平衡：

| Model | Accuracy | Precision | Recall | F1-Score | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **ResNet18 (Final)**| **95.68%** | 94.50% | **98.50%** | 96.46% | 🚀 **Deployed** |
| DenseNet121 | 96.19% | 95.82% | 96.55% | 96.18% | Comparison |
| VGG16 | 93.01% | 91.09% | 95.27% | 93.13% | Comparison |

> *注：ResNet18 虽然准确率略低于 DenseNet121，但参数量仅为 11M（vs VGG16 的 138M），训练与推理速度极快，更适合移动端部署。*

## 💻 如何运行 (How to Run)

### 1. 运行可视化看板 (最简单)
进入 `04visualization` 文件夹，直接用浏览器打开 `index.html` 即可查看完整的交互式数据报告。

### 2. 训练模型
```bash
cd 01_Code_Scripts
# 安装依赖
pip install torch torchvision pandas scikit-learn matplotlib
# 运行训练脚本
python train_model.py
```

### 3. 生成文档
```bash
# 生成最新的 Word 报告
python convert_md_to_docx.py
```

## 👥 作者 (Authors)
*   **Project Lead & Developer**: Weirui & Team
*   **Contribution**: Full-stack Development (Algorithm + Visualization + Report)

---
*Created with ❤️ for AI Healthcare*
