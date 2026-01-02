import torch
import os

# 检查模型文件
model_path = "result/best_cataract_model.pth"

print("=" * 60)
print("模型文件诊断")
print("=" * 60)

# 1. 文件基本信息
if os.path.exists(model_path):
    file_size = os.path.getsize(model_path)
    mod_time = os.path.getmtime(model_path)
    import datetime
    print(f"\n✅ 文件存在: {model_path}")
    print(f"   大小: {file_size / (1024*1024):.2f} MB")
    print(f"   修改时间: {datetime.datetime.fromtimestamp(mod_time)}")
else:
    print(f"\n❌ 文件不存在: {model_path}")
    exit(1)

# 2. 加载模型权重
try:
    checkpoint = torch.load(model_path, map_location='cpu')
    print(f"\n✅ 模型加载成功")
    
    # 检查是否是 state_dict
    if isinstance(checkpoint, dict):
        if 'state_dict' in checkpoint:
            print("   类型: 完整checkpoint（包含 state_dict）")
            state_dict = checkpoint['state_dict']
        elif 'fc.weight' in checkpoint or 'conv1.weight' in checkpoint:
            print("   类型: 纯 state_dict")
            state_dict = checkpoint
        else:
            print(f"   类型: 未知字典，键: {list(checkpoint.keys())[:5]}")
            state_dict = checkpoint
    else:
        print(f"   类型: {type(checkpoint)}")
        state_dict = None
    
    # 3. 检查关键层的权重
    if state_dict:
        print(f"\n📊 权重统计:")
        print(f"   总层数: {len(state_dict)}")
        
        # 检查最后一层 (fc) 的权重
        if 'fc.weight' in state_dict:
            fc_weight = state_dict['fc.weight']
            print(f"\n   fc.weight 形状: {fc_weight.shape}")
            print(f"   fc.weight 均值: {fc_weight.mean():.6f}")
            print(f"   fc.weight 标准差: {fc_weight.std():.6f}")
            print(f"   fc.weight 最小值: {fc_weight.min():.6f}")
            print(f"   fc.weight 最大值: {fc_weight.max():.6f}")
            
            # 判断是否为随机初始化（未训练）
            if abs(fc_weight.mean()) < 0.01 and fc_weight.std() < 0.1:
                print("\n   ⚠️  警告: fc层权重接近随机初始化，可能未训练!")
        else:
            print("\n   ❌ 未找到 fc.weight")
            
except Exception as e:
    print(f"\n❌ 模型加载失败: {e}")

print("\n" + "=" * 60)
