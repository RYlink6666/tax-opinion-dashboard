#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import subprocess

print("=" * 60)
print("Streamlit 应用诊断")
print("=" * 60)

# 1. 检查Python
print("\n[1/5] Python环境检查...", end=" ")
print(f"OK (v{sys.version.split()[0]})")

# 2. 检查streamlit
print("[2/5] Streamlit导入检查...", end=" ")
try:
    import streamlit as st
    print(f"OK (v{st.__version__})")
except ImportError as e:
    print(f"FAIL: {e}")
    sys.exit(1)

# 3. 检查数据文件
print("[3/5] 数据文件检查...", end=" ")
data_file = '../data/analysis/analysis_results.json'
if os.path.exists(data_file):
    size = os.path.getsize(data_file) / 1024
    print(f"OK ({size:.0f} KB)")
else:
    print(f"FAIL: 文件不存在")
    sys.exit(1)

# 4. 加载数据
print("[4/5] 数据加载检查...", end=" ")
try:
    sys.path.insert(0, '.')
    from utils.data_loader import load_analysis_data
    df = load_analysis_data()
    print(f"OK ({len(df)} 条)")
except Exception as e:
    print(f"FAIL: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 5. 端口检查
print("[5/5] 端口检查...", end=" ")
try:
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', 8501))
    sock.close()
    if result == 0:
        print("OCCUPIED (8501已被占用)")
        print("\n   解决方案: 关闭占用8501的进程，或使用其他端口:")
        print("   streamlit run main.py --server.port 8502 --client.email=")
    else:
        print("OK (8501端口可用)")
except Exception as e:
    print(f"SKIP: {e}")

print("\n" + "=" * 60)
print("诊断完成")
print("=" * 60)
print("\n建议:")
print("1. 确保CMD窗口中没有红色错误提示")
print("2. 如果8501端口被占用，使用其他端口: --server.port 8502")
print("3. 重新启动脚本前，关闭所有旧的CMD窗口")
print("\n下一步:")
print("  cd streamlit_app")
print("  streamlit run main.py --server.port 8501 --client.email=")
