#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
大模型训练数据可视化 - 自动化构建脚本
功能：读取Excel表格 -> 计算医学指标 -> 生成可视化数据
"""

import os
import sys
import json
import subprocess

# 自动检查并安装依赖
def check_and_install_dependencies():
    """检查并安装必要的Python包"""
    required_packages = {
        'pandas': 'pandas',
        'openpyxl': 'openpyxl'
    }
    
    missing_packages = []
    
    for package, pip_name in required_packages.items():
        try:
            __import__(package)
            print(f"✓ {package} 已安装")
        except ImportError:
            print(f"✗ {package} 未安装")
            missing_packages.append(pip_name)
    
    if missing_packages:
        print(f"\n正在安装缺失的包: {', '.join(missing_packages)}...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
            print("✓ 依赖安装完成\n")
        except subprocess.CalledProcessError as e:
            print(f"✗ 依赖安装失败: {e}")
            sys.exit(1)

# 检查依赖
check_and_install_dependencies()

import pandas as pd

# 配置
CHARTDATA_DIR = os.path.join(os.path.dirname(__file__), 'chartdata')
VISUALIZATION_DIR = os.path.join(os.path.dirname(__file__), 'visualization')
OUTPUT_JS_FILE = os.path.join(VISUALIZATION_DIR, 'js', 'data.js')

def calculate_metrics(df):
    """
    计算医学指标
    
    参数:
        df: pandas DataFrame，包含'真实类别', 'AI预测', '置信度'等列
    
    返回:
        dict: 包含各项指标的字典
    """
    # 统一大小写处理
    df['真实类别_lower'] = df['真实类别'].str.lower()
    df['AI预测_lower'] = df['AI预测'].str.lower()
    
    # 计算混淆矩阵（以Cataract为阳性）
    TP = len(df[(df['真实类别_lower'] == 'cataract') & (df['AI预测_lower'] == 'cataract')])
    TN = len(df[(df['真实类别_lower'] == 'normal') & (df['AI预测_lower'] == 'normal')])
    FP = len(df[(df['真实类别_lower'] == 'normal') & (df['AI预测_lower'] == 'cataract')])
    FN = len(df[(df['真实类别_lower'] == 'cataract') & (df['AI预测_lower'] == 'normal')])
    
    total = TP + TN + FP + FN
    
    # 计算基础指标
    accuracy = (TP + TN) / total if total > 0 else 0
    precision = TP / (TP + FP) if (TP + FP) > 0 else 0
    recall = TP / (TP + FN) if (TP + FN) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    specificity = TN / (TN + FP) if (TN + FP) > 0 else 0
    
    # 平均置信度
    avg_confidence = df['置信度'].mean()
    
    # 置信度分布（按区间统计）
    confidence_bins = [0, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    confidence_distribution = []
    for i in range(len(confidence_bins) - 1):
        count = len(df[(df['置信度'] >= confidence_bins[i]) & (df['置信度'] < confidence_bins[i+1])])
        confidence_distribution.append(count)
    # 添加1.0的情况
    confidence_distribution[-1] += len(df[df['置信度'] == 1.0])
    
    return {
        'accuracy': round(accuracy, 4),
        'precision': round(precision, 4),
        'recall': round(recall, 4),
        'f1': round(f1, 4),
        'specificity': round(specificity, 4),
        'confusion_matrix': {'TP': TP, 'TN': TN, 'FP': FP, 'FN': FN},
        'avg_confidence': round(avg_confidence, 4),
        'total': total,
        'confidence_distribution': confidence_distribution
    }

def calculate_group_metrics(df, group_name):
    """
    计算特定组别的指标
    
    参数:
        df: pandas DataFrame
        group_name: 'cataract' 或 'normal'
    
    返回:
        dict: 该组别的指标
    """
    df_group = df[df['真实类别'].str.lower() == group_name.lower()]
    
    if len(df_group) == 0:
        return {
            'precision': 0,
            'recall': 0,
            'count': 0,
            'correct': 0,
            'avg_confidence': 0
        }
    
    # 计算该组的正确预测数
    correct = len(df_group[df_group['AI预测'].str.lower() == group_name.lower()])
    
    # 对于该组的精确率和召回率
    # Precision: 在所有预测为该类的样本中，真实为该类的比例
    # Recall: 在所有真实为该类的样本中，被正确预测的比例
    
    if group_name.lower() == 'cataract':
        # 对于Cataract组（阳性）
        all_predicted_cataract = len(df[df['AI预测'].str.lower() == 'cataract'])
        precision = correct / all_predicted_cataract if all_predicted_cataract > 0 else 0
        recall = correct / len(df_group) if len(df_group) > 0 else 0
    else:
        # 对于Normal组（阴性）
        all_predicted_normal = len(df[df['AI预测'].str.lower() == 'normal'])
        precision = correct / all_predicted_normal if all_predicted_normal > 0 else 0
        recall = correct / len(df_group) if len(df_group) > 0 else 0
    
    avg_confidence = df_group['置信度'].mean()
    
    return {
        'precision': round(precision, 4),
        'recall': round(recall, 4),
        'count': len(df_group),
        'correct': correct,
        'avg_confidence': round(avg_confidence, 4)
    }

def process_excel_file(filepath, model_name):
    """
    处理单个Excel文件
    
    参数:
        filepath: Excel文件路径
        model_name: 模型名称
    
    返回:
        dict: 该模型的所有指标数据
    """
    print(f"  读取: {model_name}...")
    
    try:
        df = pd.read_excel(filepath)
        
        # 检查必要的列是否存在
        required_columns = ['真实类别', 'AI预测', '置信度']
        for col in required_columns:
            if col not in df.columns:
                print(f"    ✗ 警告: 文件缺少 '{col}' 列")
                return None
        
        # 计算整体指标
        overall_metrics = calculate_metrics(df)
        
        # 计算Cataract组指标
        cataract_metrics = calculate_group_metrics(df, 'cataract')
        
        # 计算Normal组指标
        normal_metrics = calculate_group_metrics(df, 'normal')
        
        print(f"    ✓ 准确率: {overall_metrics['accuracy']:.2%}, 样本数: {overall_metrics['total']}")
        
        return {
            'overall': overall_metrics,
            'cataract': cataract_metrics,
            'normal': normal_metrics
        }
    
    except Exception as e:
        print(f"    ✗ 错误: {e}")
        return None

def main():
    """主函数"""
    print("=" * 60)
    print("大模型训练数据可视化 - 自动化构建")
    print("=" * 60)
    print()
    
    # 检查chartdata目录
    if not os.path.exists(CHARTDATA_DIR):
        print(f"✗ 错误: 找不到数据目录 {CHARTDATA_DIR}")
        sys.exit(1)
    
    # 扫描所有Excel文件
    excel_files = [f for f in os.listdir(CHARTDATA_DIR) if f.endswith('.xlsx')]
    
    if not excel_files:
        print(f"✗ 错误: 在 {CHARTDATA_DIR} 中没有找到 .xlsx 文件")
        sys.exit(1)
    
    print(f"✓ 找到 {len(excel_files)} 个Excel文件\n")
    
    # 处理所有文件
    model_data = {}
    
    for filename in sorted(excel_files):
        filepath = os.path.join(CHARTDATA_DIR, filename)
        model_name = filename.replace('.xlsx', '')
        
        data = process_excel_file(filepath, model_name)
        if data:
            model_data[model_name] = data
    
    print()
    print(f"✓ 成功处理 {len(model_data)} 个模型的数据")
    print()
    
    # 创建visualization目录结构
    os.makedirs(os.path.join(VISUALIZATION_DIR, 'js'), exist_ok=True)
    os.makedirs(os.path.join(VISUALIZATION_DIR, 'css'), exist_ok=True)
    
    # 生成data.js文件
    print("正在生成数据文件...")
    
    js_content = f"""// 自动生成的模型数据
// 生成时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

const MODEL_DATA = {json.dumps(model_data, indent=2, ensure_ascii=False)};

// 模型列表
const MODEL_NAMES = {json.dumps(list(model_data.keys()), ensure_ascii=False)};

// 导出数据
if (typeof module !== 'undefined' && module.exports) {{
    module.exports = {{ MODEL_DATA, MODEL_NAMES }};
}}
"""
    
    with open(OUTPUT_JS_FILE, 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    print(f"✓ 数据文件已生成: {OUTPUT_JS_FILE}")
    print()
    
    # 输出统计摘要
    print("=" * 60)
    print("模型性能摘要（按准确率排序）")
    print("=" * 60)
    
    # 按准确率排序
    sorted_models = sorted(model_data.items(), key=lambda x: x[1]['overall']['accuracy'], reverse=True)
    
    print(f"{'排名':<6} {'模型名称':<20} {'准确率':<10} {'召回率':<10} {'F1分数':<10}")
    print("-" * 60)
    
    for rank, (model_name, data) in enumerate(sorted_models, 1):
        acc = data['overall']['accuracy']
        rec = data['overall']['recall']
        f1 = data['overall']['f1']
        print(f"{rank:<6} {model_name:<20} {acc:.2%}    {rec:.2%}    {f1:.2%}")
    
    print()
    print("✓ 数据处理完成！")
    print()
    print("下一步操作：")
    print("  1. 可视化页面生成中...")
    print()

if __name__ == '__main__':
    main()
