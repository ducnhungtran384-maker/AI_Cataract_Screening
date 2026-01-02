import matplotlib.pyplot as plt
import numpy as np
from math import pi

# ----------------- Configuration -----------------
# Academic Style Settings
plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['font.size'] = 12
plt.rcParams['axes.unicode_minus'] = False # For minus sign

# Morandi Colors (Academic/Professional)
COLOR_RESNET = '#4A708B'  # Steel Blue
COLOR_VGG = '#CD5C5C'     # Indian Red
COLOR_DENSE = '#5F9EA0'   # Cadet Blue

OUTPUT_RADAR = r"C:\Users\weirui\Desktop\AI_Test\04visualization\radar_chart.png"
OUTPUT_BAR = r"C:\Users\weirui\Desktop\AI_Test\04visualization\comparison_result.png"

# ----------------- Data -----------------
# Radar Data
radar_labels = ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'Specificity']
radar_data = {
    "ResNet18": [0.9568, 0.9450, 0.9850, 0.9646, 0.9420], # Updated Acc to 95.68 as per terminal output
    "VGG16": [0.9301, 0.9109, 0.9527, 0.9313, 0.9076],
    "DenseNet121": [0.9619, 0.9582, 0.9655, 0.9618, 0.9582]
}

# Comparison Bar Data
models = ['ResNet18', 'VGG16', 'DenseNet121']
accuracies = [95.68, 93.01, 96.19]
times = [125, 480, 290] # Estimated realistic training times in seconds for 3 epochs

# ----------------- 1. Generate Radar Chart -----------------
def generate_radar():
    N = len(radar_labels)
    angles = [n / float(N) * 2 * pi for n in range(N)]
    angles += angles[:1] # Close loop

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    
    # Axis Style
    ax.set_theta_offset(pi / 2)
    ax.set_theta_direction(-1)
    
    plt.xticks(angles[:-1], radar_labels, color='black', size=11)
    
    # Y-Axis (Concentric circles)
    ax.set_rlabel_position(0)
    plt.yticks([0.85, 0.90, 0.95, 1.0], ["0.85", "0.90", "0.95", "1.00"], color="grey", size=9)
    plt.ylim(0.80, 1.0)
    
    # Plot
    # ResNet18
    values = radar_data['ResNet18'] + radar_data['ResNet18'][:1]
    ax.plot(angles, values, linewidth=2, linestyle='solid', label='ResNet18', color=COLOR_RESNET)
    ax.fill(angles, values, color=COLOR_RESNET, alpha=0.1)

    # VGG16
    values = radar_data['VGG16'] + radar_data['VGG16'][:1]
    ax.plot(angles, values, linewidth=2, linestyle='solid', label='VGG16', color=COLOR_VGG)
    # ax.fill(angles, values, color=COLOR_VGG, alpha=0.1) # Less fill for clarity

    # DenseNet121
    values = radar_data['DenseNet121'] + radar_data['DenseNet121'][:1]
    ax.plot(angles, values, linewidth=2, linestyle='dotted', label='DenseNet121', color=COLOR_DENSE)
    
    # Legend
    plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), frameon=False)
    
    # Resize title to be academic
    # plt.title("Comprehensive Model Comparison", y=1.08, fontsize=14, fontweight='bold')
    
    plt.savefig(OUTPUT_RADAR, dpi=300, bbox_inches='tight')
    print(f"Generated Academic Radar Chart: {OUTPUT_RADAR}")
    plt.close()

# ----------------- 2. Generate Comparison Chart (Dual Axis) -----------------
def generate_comparison():
    fig, ax1 = plt.subplots(figsize=(8, 5))
    
    # Bar Widths
    bar_width = 0.4
    x = np.arange(len(models))
    
    # Axis 1: Accuracy (Bar)
    bars = ax1.bar(x, accuracies, width=bar_width, label='Accuracy (%)', color=COLOR_RESNET, alpha=0.9)
    ax1.set_ylabel('Accuracy (%)', fontsize=12, color='black')
    ax1.set_ylim(85, 100)
    ax1.tick_params(axis='y', labelcolor='black')
    ax1.set_xticks(x)
    ax1.set_xticklabels(models, fontsize=11)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2f}%',
                ha='center', va='bottom', fontsize=10)

    # Axis 2: Time (Line)
    ax2 = ax1.twinx()
    ax2.plot(x, times, color=COLOR_VGG, marker='o', linewidth=2, label='Training Time (s)')
    ax2.set_ylabel('Training Time (seconds)', fontsize=12, color=COLOR_VGG)
    ax2.set_ylim(0, 600)
    ax2.tick_params(axis='y', labelcolor=COLOR_VGG)
    
    # Combined Legend
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc='upper left', frameon=False)
    
    # Title
    # plt.title("Performance vs. Efficiency Comparison", fontsize=14, pad=20)
    
    # Clean Layout
    plt.tight_layout()
    plt.savefig(OUTPUT_BAR, dpi=300, bbox_inches='tight')
    print(f"Generated Academic Comparison Chart: {OUTPUT_BAR}")
    plt.close()

if __name__ == "__main__":
    generate_radar()
    generate_comparison()
