"""
离线预训练BERTopic模型
在本地训练一次，保存模型和结果，然后上传到云端
这样P7页面加载时无需重新训练，直接秒开
"""

import sys
import os

# === 在导入任何库之前设置HuggingFace镜像源 ===
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
os.environ['HF_HOME'] = os.path.expanduser('~/.cache/huggingface')

import pickle
import json
import pandas as pd
import numpy as np
from pathlib import Path

# 添加streamlit_app到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'streamlit_app'))

# 设置UTF-8编码
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from utils.data_loader import load_analysis_data
from utils.bertopic_analyzer import get_bertopic_model

print("=" * 60)
print("BERTopic offline pretraining script")
print("=" * 60)
print()

# 1. 加载数据
print("1. Loading data...")
try:
    df = load_analysis_data()
    texts = df['source_text'].tolist()
    print(f"   OK: Loaded {len(texts)} opinions")
except Exception as e:
    print(f"   ERROR: {e}")
    sys.exit(1)

# 2. 初始化BERTopic模型
print()
print("2. Initializing BERTopic model...")
try:
    print("   DEBUG: Attempting to get BERTopic model...")
    model = get_bertopic_model()
    print(f"   DEBUG: Model returned: {model}")
    if model is None:
        print("   ERROR: Model initialization failed (returned None)")
        sys.exit(1)
    print("   OK: Model initialized")
except Exception as e:
    print(f"   ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 3. 训练模型
print()
print("3. Training BERTopic model (this will take 3-5 minutes)...")
try:
    topics, probs = model.fit_transform(texts)
    print(f"   OK: Training complete! Found {len(np.unique(topics))} topics")
except Exception as e:
    print(f"   ERROR: {e}")
    sys.exit(1)

# 4. 保存模型
print()
print("4. Saving model...")
model_dir = Path(__file__).parent / "streamlit_app" / "data" / "bertopic_model"

# 强制删除旧目录（如果存在）
import shutil
if model_dir.exists():
    try:
        shutil.rmtree(str(model_dir), ignore_errors=True)
        print(f"   Cleaned old model directory")
    except:
        pass

# 重新创建目录
try:
    model_dir.mkdir(parents=True, exist_ok=True)
    import os
    os.chmod(str(model_dir), 0o777)  # 设置完全权限
    print(f"   Model directory ready: {model_dir}")
except Exception as e:
    print(f"   ERROR creating directory: {e}")
    sys.exit(1)

try:
    # 用pickle保存BERTopic模型（避免BERTopic.save()的bug）
    model_file = model_dir / "model.pkl"
    with open(model_file, 'wb') as f:
        pickle.dump(model, f)
    print(f"   OK: Model saved to {model_file}")
except Exception as e:
    print(f"   ERROR saving: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 5. 保存话题结果
print()
print("5. Saving topic analysis results...")
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
    
    print(f"   OK: Results saved to {result_file}")
except Exception as e:
    print(f"   ERROR: {e}")

# 6. 显示统计信息
print()
print("=" * 60)
print("Pretraining Results Summary")
print("=" * 60)
print()
print(f"Total documents: {len(texts)}")
print(f"Discovered topics: {len(np.unique(topics))}")
print(f"Noise documents (-1): {np.sum(topics == -1)}")
print()

# 显示主题信息
topic_info = model.get_topic_info()
print("Topic distribution:")
print(topic_info[['Topic', 'Count', 'Name']].to_string(index=False))
print()

print("=" * 60)
print("OK: Pretraining complete!")
print()
print("Next steps:")
print("   1. Upload streamlit_app/data/bertopic_model/ to GitHub")
print("   2. git push origin main")
print("   3. Wait 2-3 minutes for Streamlit Cloud to deploy")
print("   4. P7 page will load instantly without training")
print()
print("=" * 60)
