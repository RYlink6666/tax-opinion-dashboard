#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
离线训练BERTopic模型并保存
在本地运行一次，生成预训练模型文件
然后上传到GitHub供Cloud使用
"""

import os
import json
import pickle
import sys
from pathlib import Path

# 修复Windows编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='ignore')

def train_and_save_model():
    """训练BERTopic模型并保存为文件"""
    
    print("=" * 70)
    print("[BERTopic 离线训练]")
    print("=" * 70)
    
    # 1. 加载数据
    print("\n[1/4] 加载数据文件...")
    data_path = "data/analysis/analysis_results.json"
    
    if not os.path.exists(data_path):
        print(f"[错误] 找不到数据文件: {data_path}")
        return False
    
    try:
        with open(data_path, 'r', encoding='utf-8', errors='ignore') as f:
            data = json.load(f)
        
        texts = [item.get('source_text', '') for item in data.get('data', [])]
        texts = [t for t in texts if t.strip()]  # 去除空值
        
        print(f"    [OK] 已加载 {len(texts)} 条文本")
    except Exception as e:
        print(f"[ERROR] 加载数据失败: {e}")
        return False
    
    # 2. 导入BERTopic
    print("\n[2/4] 导入BERTopic模块...")
    try:
        from bertopic import BERTopic
        from sentence_transformers import SentenceTransformer
        print("    [OK] BERTopic 导入成功")
    except ImportError as e:
        print(f"[ERROR] BERTopic未安装: {e}")
        print("    运行: pip install bertopic sentence-transformers")
        return False
    
    # 3. 训练模型
    print("\n[3/4] 训练BERTopic模型（这需要几分钟...）")
    try:
        # 使用轻量中文模型
        print("    [STEP] 加载embedding模型...")
        try:
            embedding_model = SentenceTransformer('shibing624/text2vec-base-chinese')
            model_source = "轻量中文模型"
        except:
            embedding_model = SentenceTransformer('distiluse-base-multilingual-cased-v2')
            model_source = "多语言模型"
        
        print(f"    [STEP] 使用: {model_source}")
        print("    [STEP] 训练主题模型...")
        
        model = BERTopic(
            embedding_model=embedding_model,
            language="chinese",
            calculate_probabilities=True,
            verbose=True
        )
        
        topics, probs = model.fit_transform(texts)
        print(f"    [OK] 模型训练完成")
        print(f"    [INFO] 发现主题数: {model.get_topic_freq().shape[0]}")
        
    except Exception as e:
        print(f"[ERROR] 模型训练失败: {e}")
        return False
    
    # 4. 保存模型
    print("\n[4/4] 保存模型文件...")
    try:
        # 创建models目录
        os.makedirs("streamlit_app/models", exist_ok=True)
        
        model_path = "streamlit_app/models/bertopic_model.pkl"
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        
        file_size = os.path.getsize(model_path) / (1024 * 1024)  # MB
        print(f"    [OK] 模型已保存")
        print(f"    [INFO] 路径: {model_path}")
        print(f"    [INFO] 大小: {file_size:.1f} MB")
        
    except Exception as e:
        print(f"[ERROR] 模型保存失败: {e}")
        return False
    
    print("\n" + "=" * 70)
    print("[SUCCESS] 预训练模型已生成!")
    print("=" * 70)
    print(f"""
下一步：
1. 提交模型文件到Git:
   git add streamlit_app/models/
   git commit -m "Add pretrained BERTopic model for instant Cloud deployment"
   git push origin main

2. Streamlit Cloud将自动使用预训练模型
   首次加载: 秒开 (无需训练)
   用户体验: 极速
""")
    
    return True

if __name__ == "__main__":
    success = train_and_save_model()
    sys.exit(0 if success else 1)
