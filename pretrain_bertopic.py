"""
离线预训练BERTopic模型
在本地训练一次，保存模型和结果，然后上传到云端
这样P7页面加载时无需重新训练，直接秒开
"""

import sys
import os
import pickle
import json
import pandas as pd
import numpy as np
from pathlib import Path

# 添加streamlit_app到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'streamlit_app'))

from utils.data_loader import load_analysis_data
from utils.bertopic_analyzer import get_bertopic_model

print("=" * 60)
print("🚀 BERTopic 离线预训练脚本")
print("=" * 60)
print()

# 1. 加载数据
print("1️⃣  加载数据...")
try:
    df = load_analysis_data()
    texts = df['source_text'].tolist()
    print(f"   ✅ 已加载 {len(texts)} 条舆论")
except Exception as e:
    print(f"   ❌ 加载失败: {e}")
    sys.exit(1)

# 2. 初始化BERTopic模型
print()
print("2️⃣  初始化BERTopic模型...")
try:
    model = get_bertopic_model()
    if model is None:
        print("   ❌ 模型初始化失败")
        sys.exit(1)
    print("   ✅ 模型初始化成功")
except Exception as e:
    print(f"   ❌ 初始化失败: {e}")
    sys.exit(1)

# 3. 训练模型
print()
print("3️⃣  训练BERTopic模型（这会花费3-5分钟）...")
try:
    topics, probs = model.fit_transform(texts)
    print(f"   ✅ 训练完成！发现 {len(np.unique(topics))} 个主题")
except Exception as e:
    print(f"   ❌ 训练失败: {e}")
    sys.exit(1)

# 4. 保存模型
print()
print("4️⃣  保存模型...")
model_dir = Path(__file__).parent / "streamlit_app" / "data" / "bertopic_model"
model_dir.mkdir(parents=True, exist_ok=True)

try:
    # 保存BERTopic模型
    model.save(str(model_dir))
    print(f"   ✅ 模型已保存到: {model_dir}")
except Exception as e:
    print(f"   ❌ 保存失败: {e}")
    sys.exit(1)

# 5. 保存话题结果
print()
print("5️⃣  保存话题分析结果...")
try:
    results = {
        'topics': topics.tolist(),
        'probabilities': probs.tolist() if probs is not None else None,
        'topic_info': model.get_topic_info().to_dict(orient='records'),
        'num_topics': len(np.unique(topics)),
        'num_documents': len(texts)
    }
    
    result_file = model_dir / "topics_result.json"
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"   ✅ 结果已保存到: {result_file}")
except Exception as e:
    print(f"   ❌ 保存结果失败: {e}")

# 6. 显示统计信息
print()
print("=" * 60)
print("📊 预训练结果统计")
print("=" * 60)
print()
print(f"总文档数: {len(texts)}")
print(f"发现的主题数: {len(np.unique(topics))}")
print(f"噪声文档 (-1): {np.sum(topics == -1)}")
print()

# 显示主题信息
topic_info = model.get_topic_info()
print("主题分布:")
print(topic_info[['Topic', 'Count', 'Name']].to_string(index=False))
print()

print("=" * 60)
print("✅ 预训练完成！")
print()
print("📝 后续步骤:")
print("   1. 将生成的 streamlit_app/data/bertopic_model/ 文件夹上传到GitHub")
print("   2. 修改P7页面，改用预训练模型而不是每次重新训练")
print("   3. P7页面会秒开，无需等待训练")
print()
print("=" * 60)
