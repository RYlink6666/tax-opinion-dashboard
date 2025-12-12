"""
简化版 BERTopic 预训练 - 不需要 PyTorch
使用 TF-IDF + HDBSCAN 进行话题建模
"""

import sys
import os
import pickle
import json
import pandas as pd
import numpy as np
from pathlib import Path

# 添加 streamlit_app 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'streamlit_app'))

# 设置 UTF-8 编码
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from utils.data_loader import load_analysis_data

print("=" * 60)
print("Simplified BERTopic (TF-IDF + HDBSCAN)")
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

# 2. TF-IDF 向量化
print()
print("2. Computing TF-IDF vectors...")
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    
    vectorizer = TfidfVectorizer(
        max_features=500,
        min_df=2,
        max_df=0.8,
        ngram_range=(1, 2),
        stop_words=None  # 中文不用英文停用词
    )
    
    tfidf_matrix = vectorizer.fit_transform(texts)
    print(f"   OK: Generated {tfidf_matrix.shape[1]} TF-IDF features")
except Exception as e:
    print(f"   ERROR: {e}")
    sys.exit(1)

# 3. UMAP 降维
print()
print("3. Reducing dimensionality with UMAP...")
try:
    from umap import UMAP
    
    umap_model = UMAP(
        n_neighbors=15,
        n_components=5,
        min_dist=0.1,
        metric='cosine',
        random_state=42
    )
    
    reduced_embeddings = umap_model.fit_transform(tfidf_matrix.toarray())
    print(f"   OK: Reduced to {reduced_embeddings.shape[1]} dimensions")
except Exception as e:
    print(f"   ERROR: {e}")
    sys.exit(1)

# 4. HDBSCAN 聚类
print()
print("4. Clustering with HDBSCAN...")
try:
    from hdbscan import HDBSCAN
    
    hdbscan_model = HDBSCAN(
        min_cluster_size=20,
        min_samples=5,
        metric='euclidean'
    )
    
    topics = hdbscan_model.fit_predict(reduced_embeddings)
    n_topics = len(set(topics)) - 1  # 不计噪声 (-1)
    print(f"   OK: Found {n_topics} topics")
except Exception as e:
    print(f"   ERROR: {e}")
    sys.exit(1)

# 5. 生成话题标签
print()
print("5. Generating topic labels...")
try:
    # 对每个话题提取 Top 5 词
    feature_names = vectorizer.get_feature_names_out()
    topic_labels = {}
    
    for topic_id in sorted(set(topics)):
        if topic_id == -1:  # 噪声
            continue
        
        # 获取该话题的文档
        mask = topics == topic_id
        topic_docs = tfidf_matrix[mask]
        
        # 计算该话题中词的平均 TF-IDF
        mean_tfidf = np.asarray(topic_docs.mean(axis=0)).ravel()
        top_indices = mean_tfidf.argsort()[-5:][::-1]
        
        top_words = [feature_names[i] for i in top_indices]
        topic_labels[topic_id] = f"话题{int(topic_id)}: " + ", ".join(top_words)
    
    print(f"   OK: Generated {len(topic_labels)} topic labels")
except Exception as e:
    print(f"   ERROR: {e}")
    topic_labels = {i: f"话题{i}" for i in set(topics) if i != -1}

# 6. 保存结果
print()
print("6. Saving results...")
model_dir = Path(__file__).parent / "streamlit_app" / "data" / "bertopic_model"
model_dir.mkdir(parents=True, exist_ok=True)

try:
    # 保存关键模型文件
    with open(model_dir / "tfidf_vectorizer.pkl", 'wb') as f:
        pickle.dump(vectorizer, f)
    
    with open(model_dir / "umap_model.pkl", 'wb') as f:
        pickle.dump(umap_model, f)
    
    with open(model_dir / "hdbscan_model.pkl", 'wb') as f:
        pickle.dump(hdbscan_model, f)
    
    # 保存结果
    results = {
        'topics': topics.tolist(),
        'topic_labels': {str(k): v for k, v in topic_labels.items()},
        'num_topics': n_topics,
        'num_documents': len(texts),
        'num_noise': int(np.sum(topics == -1)),
        'method': 'TF-IDF + HDBSCAN'
    }
    
    with open(model_dir / "topics_result.json", 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"   OK: Results saved to {model_dir}")
except Exception as e:
    print(f"   ERROR: {e}")
    sys.exit(1)

# 7. 显示统计
print()
print("=" * 60)
print("Pretraining Results Summary")
print("=" * 60)
print()
print(f"Total documents: {len(texts)}")
print(f"Discovered topics: {n_topics}")
print(f"Noise documents: {np.sum(topics == -1)}")
print()

print("Topics:")
for topic_id, label in sorted(topic_labels.items()):
    count = np.sum(topics == topic_id)
    print(f"  {label} ({count} docs)")

print()
print("=" * 60)
print("OK: Pretraining complete!")
print()
print("Next steps:")
print("   1. Upload streamlit_app/data/bertopic_model/ to GitHub")
print("   2. git push origin main")
print()
print("=" * 60)
