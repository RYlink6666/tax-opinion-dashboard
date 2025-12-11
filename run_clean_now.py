#!/usr/bin/env python3
"""
快速运行数据清洁脚本
"""
import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file__))

# 导入并运行
from merge_and_clean import main

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
