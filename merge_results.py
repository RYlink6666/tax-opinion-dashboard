#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合并前900条和后1399条结果成完整文件
"""

import json
import sys
from pathlib import Path

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 说明：
# 1. 前900条数据从第一次不完整的运行中获取（已停止）
# 2. 后1399条数据从 analysis_results.json 中获取（刚完成）
# 3. 需要从原始数据中提取前900条进行重新分析

print("=" * 70)
print("[MERGE] Combining analysis results")
print("=" * 70)
print()

# 加载原始意见数据
INPUT_FILE = Path("data/clean/opinions_clean_5000.txt")
PARTIAL_FILE = Path("data/analysis/analysis_results.json")
OUTPUT_FILE = Path("data/analysis/analysis_results_complete.json")

print("[1] Loading original opinions...")
with open(INPUT_FILE, 'r', encoding='utf-8') as f:
    all_opinions = [line.strip() for line in f if line.strip()]
print(f"[OK] Loaded {len(all_opinions)} total opinions\n")

print("[2] Loading partial results (900-2299)...")
with open(PARTIAL_FILE, 'r', encoding='utf-8') as f:
    partial_data = json.load(f)
print(f"[OK] Loaded {partial_data['total']} partial results\n")

# 现在需要用新的API重新分析前900条
print("[3] 需要重新分析前900条 (0-899)")
print("    由于前次中断，前900条的数据丢失了")
print("    需要从头重新分析或从之前的备份恢复\n")

print("=" * 70)
print("[OPTIONS]")
print("=" * 70)
print("""
选项A：使用已完成的1399条数据（900-2299）
  - 当前有完整的后1399条分析结果
  - 前900条需要单独处理
  
选项B：重新完整分析全部2299条
  - 修改脚本 START_IDX = 0
  - 重新运行 python llm_analyze.py
  - 这样会得到完整的2299条分析

选项C：使用不完整数据（952条已分析 + 1399条已分析）
  - 总共2351条，有重复但不是100%覆盖
""")

print("\n[RECOMMENDATION] 推荐选项B：重新完整分析全部2299条")
print("修改脚本后再运行一次，确保数据完整")
