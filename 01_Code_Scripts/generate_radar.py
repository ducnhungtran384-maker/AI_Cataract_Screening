import numpy as np
import matplotlib.pyplot as plt
from math import pi

# Data from model_comparison.js
labels = ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'Specificity']
models = {
    "ResNet18": [0.9485, 0.9100, 0.9949, 0.9506, 0.9025],
    "VGG16": [0.9301, 0.9109, 0.9527, 0.9313, 0.9076],
    "DenseNet121": [0.9619, 0.9582, 0.9655, 0.9618, 0.9582]
}
colors = {"ResNet18": '#3498db', "VGG16": '#e74c3c', "DenseNet121": '#2ecc71'}

def make_radar_chart():
    N = len(labels)
    
    # What will be the angle of each axis in the plot? (we divide the plot / number of variable)
    angles = [n / float(N) * 2 * pi for n in range(N)]
    angles += angles[:1]
    
    # Initialize the spider plot
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    
    # Draw one axe per variable + add labels
    plt.xticks(angles[:-1], labels, color='black', size=10)
    
    # Draw ylabels
    ax.set_rlabel_position(0)
    plt.yticks([0.8, 0.85, 0.9, 0.95, 1.0], ["0.80", "0.85", "0.90", "0.95", "1.00"], color="grey", size=8)
    plt.ylim(0.8, 1.0)
    
    # Plot data
    for name, data in models.items():
        values = data + data[:1]
        ax.plot(angles, values, linewidth=2, linestyle='solid', label=name, color=colors[name])
        ax.fill(angles, values, color=colors[name], alpha=0.1)
    
    # Add legend
    plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
    
    plt.title('Comprehensive Model Performance Comparison (Radar Chart)', size=14, y=1.1)
    
    output_path = r"C:\Users\weirui\Desktop\AI_Test\04visualization\radar_chart.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Details: Generated radar chart at {output_path}")

if __name__ == "__main__":
    make_radar_chart()
