#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析现有1399条结果的统计数据
"""

import json
import sys
from pathlib import Path
from collections import Counter

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

INPUT_FILE = Path("data/analysis/analysis_results.json")

print("=" * 70)
print("[ANALYSIS] Existing results (1399 opinions)")
print("=" * 70)
print()

# 加载数据
with open(INPUT_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

results = data['data']
total = len(results)

print(f"[INFO] Total records: {total}\n")

# 1. 情感分析
print("[1] SENTIMENT Distribution")
print("-" * 70)
sentiments = Counter(r.get('sentiment', 'unknown') for r in results)
for sent, count in sorted(sentiments.items(), key=lambda x: -x[1]):
    pct = 100 * count / total
    bar = "█" * int(pct / 2)
    print(f"  {sent:10s}: {count:4d} ({pct:5.1f}%) {bar}")

avg_conf = sum(r.get('sentiment_confidence', 0) for r in results) / total
print(f"  Avg confidence: {avg_conf:.2f}\n")

# 2. 话题分析
print("[2] TOPIC Distribution (Top 8)")
print("-" * 70)
topics = Counter(r.get('topic', 'unknown') for r in results)
for topic, count in topics.most_common(8):
    pct = 100 * count / total
    bar = "█" * int(pct / 2)
    print(f"  {topic:20s}: {count:4d} ({pct:5.1f}%) {bar}")
print()

# 3. 风险等级
print("[3] RISK LEVEL Distribution")
print("-" * 70)
risks = Counter(r.get('risk_level', 'unknown') for r in results)
risk_order = ['critical', 'high', 'medium', 'low']
for risk in risk_order:
    count = risks.get(risk, 0)
    pct = 100 * count / total
    bar = "█" * int(pct / 2)
    print(f"  {risk:10s}: {count:4d} ({pct:5.1f}%) {bar}")
print()

# 4. 参与方
print("[4] ACTOR Distribution")
print("-" * 70)
actors = Counter(r.get('actor', 'unknown') for r in results)
for actor, count in sorted(actors.items(), key=lambda x: -x[1]):
    pct = 100 * count / total
    bar = "█" * int(pct / 2)
    print(f"  {actor:25s}: {count:4d} ({pct:5.1f}%) {bar}")
print()

# 5. 模式分析
print("[5] PATTERN Distribution (Top 8)")
print("-" * 70)
patterns = Counter(r.get('pattern', 'unknown') for r in results)
for pattern, count in patterns.most_common(8):
    pct = 100 * count / total
    bar = "█" * int(pct / 2)
    print(f"  {pattern:15s}: {count:4d} ({pct:5.1f}%) {bar}")
print()

# 6. 置信度汇总
print("[6] CONFIDENCE Summary")
print("-" * 70)
conf_types = {
    'sentiment': [r.get('sentiment_confidence', 0) for r in results],
    'topic': [r.get('topic_confidence', 0) for r in results],
    'pattern': [r.get('pattern_confidence', 0) for r in results],
    'risk': [r.get('risk_confidence', 0) for r in results],
    'actor': [r.get('actor_confidence', 0) for r in results],
}

for conf_type, values in conf_types.items():
    avg = sum(values) / len(values) if values else 0
    print(f"  {conf_type:15s}: {avg:.2f}")
print()

# 7. 典型案例
print("[7] SAMPLE Cases")
print("-" * 70)
print("\n[负面情感案例]")
negatives = [r for r in results if r.get('sentiment') == 'negative']
if negatives:
    sample = negatives[0]
    print(f"  Text: {sample['source_text'][:80]}")
    print(f"  Topic: {sample['topic']}")
    print(f"  Risk: {sample['risk_level']}")
    print(f"  Summary: {sample['brief_summary']}\n")

print("[正面情感案例]")
positives = [r for r in results if r.get('sentiment') == 'positive']
if positives:
    sample = positives[0]
    print(f"  Text: {sample['source_text'][:80]}")
    print(f"  Topic: {sample['topic']}")
    print(f"  Risk: {sample['risk_level']}")
    print(f"  Summary: {sample['brief_summary']}\n")

print("=" * 70)
print(f"[OK] Analysis complete")
print(f"[DATA] {INPUT_FILE}")
print("=" * 70)
