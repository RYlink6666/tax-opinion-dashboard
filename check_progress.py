#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查Phase 2分析进度（不中断主任务）
"""

import json
import sys
from pathlib import Path

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def check_file(filepath):
    """检查文件状态"""
    p = Path(filepath)
    if not p.exists():
        return {"status": "not_started", "size": 0}
    
    size = p.stat().st_size
    
    # 尝试读取并解析
    try:
        with open(p, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return {
                "status": "completed" if data.get("total", 0) > 0 else "in_progress",
                "size": size,
                "total": data.get("total", 0),
                "success_rate": data.get("success_rate", "0%"),
                "data_count": len(data.get("data", []))
            }
    except:
        return {"status": "in_progress", "size": size}

print("=" * 70)
print("[PROGRESS CHECK] Phase 2 LLM Analysis")
print("=" * 70)
print()

# 检查各个阶段
checks = {
    "快速测试 (10条)": "data/analysis/sample_10_results.json",
    "样本测试 (100条)": "data/analysis/sample_100_results.json",
    "全量分析 (2,313条)": "data/analysis/analysis_results.json"
}

for name, filepath in checks.items():
    result = check_file(filepath)
    status = result.get("status", "?")
    size = result.get("size", 0)
    
    print(f"[{name}]")
    print(f"  Status: {status}")
    print(f"  File size: {size:,} bytes")
    
    if "total" in result:
        print(f"  Progress: {result['total']} analyzed")
        print(f"  Success rate: {result['success_rate']}")
    
    print()

# 检查源数据
print("[数据源]")
input_file = Path("data/clean/opinions_clean_5000.txt")
if input_file.exists():
    with open(input_file, 'r', encoding='utf-8') as f:
        opinions = [line.strip() for line in f if line.strip()]
    print(f"  清洁意见总数: {len(opinions)}")
else:
    print(f"  清洁意见文件不存在")

print()
print("=" * 70)
