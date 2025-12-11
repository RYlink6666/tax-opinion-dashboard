#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证数据状态脚本
检查缺失记录数和覆盖率
"""

import json
import sys
from pathlib import Path

# 处理Windows编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PROJECT_ROOT = Path(__file__).parent
CLEAN_DATA_FILE = PROJECT_ROOT / "data" / "clean" / "opinions_clean_5000.json"
ANALYSIS_FILE = PROJECT_ROOT / "data" / "analysis" / "analysis_results.json"

def main():
    print("\n" + "="*60)
    print("📊 数据状态检查")
    print("="*60)
    
    # 加载数据
    print("\n🔍 加载数据...")
    
    with open(CLEAN_DATA_FILE, 'r', encoding='utf-8') as f:
        clean_data = json.load(f)
    clean_opinions = clean_data.get('data', [])
    
    with open(ANALYSIS_FILE, 'r', encoding='utf-8') as f:
        analysis_data = json.load(f)
    analyzed_results = analysis_data.get('data', [])
    
    # 统计
    clean_count = len(clean_opinions)
    analyzed_count = len(analyzed_results)
    
    # 找缺失的
    analyzed_texts = {r.get('source_text') for r in analyzed_results if r.get('source_text')}
    missing_count = 0
    for op in clean_opinions:
        content = op.get('content') if isinstance(op, dict) else op
        if content and content not in analyzed_texts:
            missing_count += 1
    
    coverage = (analyzed_count / clean_count * 100) if clean_count > 0 else 0
    
    # 显示结果
    print(f"\n✅ 原始数据: {clean_count:,} 条")
    print(f"✅ 已分析: {analyzed_count:,} 条")
    print(f"❌ 缺失: {missing_count:,} 条")
    print(f"📊 覆盖率: {coverage:.1f}%")
    
    # 预测完成时间
    if missing_count > 0:
        est_time_minutes = int(missing_count / 4)  # 约每分钟4条
        print(f"\n⏱️  预估分析时间: {est_time_minutes} 分钟")
        print(f"   (基于4条/分钟的速率)")
    
    # 显示最后更新时间
    last_updated = analysis_data.get('last_updated', 'unknown')
    print(f"\n🕐 最后更新: {last_updated}")
    
    # 显示model信息
    model = analysis_data.get('model', 'unknown')
    api_prefix = analysis_data.get('api_key_prefix', 'unknown')
    print(f"🤖 使用模型: {model}")
    print(f"🔑 API密钥前缀: {api_prefix}")
    
    print("\n" + "="*60)
    
    if missing_count == 0:
        print("✨ 所有数据都已分析！")
    else:
        print(f"💡 运行以下命令开始分析:")
        print(f"   python analyze_missing_900.py")
        print(f"   或双击 analyze_missing_900.bat")
    
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
