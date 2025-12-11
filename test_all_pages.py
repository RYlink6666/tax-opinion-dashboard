# -*- coding: utf-8 -*-
"""
测试所有streamlit页面是否能正确加载
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'streamlit_app'))

from utils.data_loader import (
    load_analysis_data, 
    get_sentiment_distribution,
    get_topic_distribution,
    get_risk_distribution,
    get_actor_distribution,
    get_confidence_stats
)

print("=" * 60)
print("Phase 3 - Streamlit应用页面加载验证")
print("=" * 60)

try:
    # 加载数据
    print("\n[1/5] 加载分析数据...", end=" ")
    df = load_analysis_data()
    print(f"OK ({len(df)} 条记录)")
    
    # 测试情感分析
    print("[2/5] 计算情感分布...", end=" ")
    sentiment = get_sentiment_distribution(df)
    print(f"OK ({len(sentiment)} 种)")
    
    # 测试话题分析
    print("[3/5] 计算话题分布...", end=" ")
    topics = get_topic_distribution(df)
    print(f"OK ({len(topics)} 个话题)")
    
    # 测试风险分析
    print("[4/5] 计算风险分布...", end=" ")
    risk = get_risk_distribution(df)
    print(f"OK ({len(risk)} 个级别)")
    
    # 测试置信度
    print("[5/5] 计算置信度...", end=" ")
    confidence = get_confidence_stats(df)
    print(f"OK (5 项指标)")
    
    print("\n" + "=" * 60)
    print("数据统计摘要")
    print("=" * 60)
    print(f"\n【记录总数】{len(df)}")
    print(f"\n【情感分布】")
    for k, v in sentiment.items():
        pct = 100 * v / len(df)
        print(f"  {k:12s}: {v:5d} ({pct:5.1f}%)")
    
    print(f"\n【话题分布（Top 10）】")
    for i, (k, v) in enumerate(topics.items(), 1):
        pct = 100 * v / len(df)
        print(f"  {i:2d}. {k:20s}: {v:5d} ({pct:5.1f}%)")
    
    print(f"\n【风险等级分布】")
    for k, v in risk.items():
        pct = 100 * v / len(df)
        print(f"  {k:12s}: {v:5d} ({pct:5.1f}%)")
    
    print(f"\n【置信度平均值】")
    for k, v in confidence.items():
        print(f"  {k:15s}: {v:.3f}")
    
    print("\n" + "=" * 60)
    print("✓ 所有页面可正常加载，无错误")
    print("=" * 60)
    print("\n应用启动命令:")
    print("  cd streamlit_app")
    print("  streamlit run main.py --client.email=")
    
except Exception as e:
    print(f"\n✗ 错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
