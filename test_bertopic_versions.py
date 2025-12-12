"""
快速版本兼容性测试（不进行训练）
验证 BERTopic + PyTorch 能否正确导入
"""

import sys
import os

# 设置UTF-8编码
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 60)
print("BERTopic Version Compatibility Test")
print("=" * 60)
print()

# 测试PyTorch
print("1. Testing PyTorch...")
try:
    import torch
    print(f"   OK torch: {torch.__version__}")
except ImportError as e:
    print(f"   ERROR torch: {e}")
    sys.exit(1)

# 测试transformers
print()
print("2. Testing transformers...")
try:
    import transformers
    print(f"   OK transformers: {transformers.__version__}")
except ImportError as e:
    print(f"   ERROR transformers: {e}")
    sys.exit(1)

# 测试sentence-transformers
print()
print("3. Testing sentence-transformers...")
try:
    from sentence_transformers import SentenceTransformer
    print(f"   OK sentence-transformers: imported successfully")
except ImportError as e:
    print(f"   ERROR sentence-transformers: {e}")
    sys.exit(1)

# 测试BERTopic
print()
print("4. Testing BERTopic...")
try:
    from bertopic import BERTopic
    print(f"   OK BERTopic: imported successfully")
except ImportError as e:
    print(f"   ERROR BERTopic: {e}")
    sys.exit(1)

# 测试其他依赖
print()
print("5. Testing other dependencies...")
try:
    import umap
    import hdbscan
    import sklearn
    print(f"   OK umap: imported")
    print(f"   OK hdbscan: imported")
    print(f"   OK scikit-learn: {sklearn.__version__}")
except ImportError as e:
    print(f"   ERROR dependency: {e}")
    sys.exit(1)

print()
print("=" * 60)
print("All version checks passed!")
print("=" * 60)
print()
print("Ready to run: python pretrain_bertopic.py")
