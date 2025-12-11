#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试 - 仅测10条舆论
"""

import json
import sys
from pathlib import Path

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

INPUT_FILE = Path("data/clean/opinions_clean_5000.txt")
OUTPUT_FILE = Path("data/analysis/sample_10_results.json")
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

API_KEY = "91cff4bec1fe4bdfa2cb35fc5ca03002.YngoEUjQqKF0f6qN"
MODEL = "glm-4-flash"

SYSTEM_PROMPT = """你是一个专业的跨境电商税收舆论分析系统。请对用户提供的舆论进行以下5个维度的结构化分析。

分析维度：
1. sentiment: positive|neutral|negative
2. topic: tax_policy|price_impact|compliance|business_risk|advocacy|other
3. pattern: 0110|9610|9710|9810|1039|Temu|multiple|unknown
4. risk_level: critical|high|medium|low
5. actor: enterprise|consumer|government|cross_border_seller|general_public|multiple

返回JSON格式（必须有效）：
{
    "sentiment": "positive|neutral|negative",
    "sentiment_confidence": 0.85,
    "topic": "...",
    "topic_confidence": 0.90,
    "pattern": "...",
    "pattern_confidence": 0.75,
    "risk_level": "...",
    "risk_confidence": 0.88,
    "actor": "...",
    "actor_confidence": 0.80,
    "key_phrase": "关键短语",
    "brief_summary": "简短总结"
}"""

def call_api(text):
    """调用智谱API"""
    try:
        from zhipuai import ZhipuAI
        client = ZhipuAI(api_key=API_KEY)
        
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"分析：{text}"}
            ],
            temperature=0.3,
            top_p=0.8,
        )
        
        result_text = response.choices[0].message.content
        
        # 提取JSON (可能被markdown代码块包装)
        if result_text.startswith("```"):
            start = result_text.find('\n') + 1
            end = result_text.rfind('```')
            result_text = result_text[start:end].strip()
        
        return json.loads(result_text)
    except Exception as e:
        return None

print("=" * 70)
print("[QUICK TEST] 10 opinions")
print("=" * 70)
print()

print("[1] Loading opinions...")
with open(INPUT_FILE, 'r', encoding='utf-8') as f:
    all_opinions = [line.strip() for line in f if line.strip()]

sample = all_opinions[:10]
print(f"[OK] Loaded {len(sample)} opinions\n")

print("[2] Analyzing...")
results = []

for idx, opinion in enumerate(sample, 1):
    print(f"[{idx}/10] Analyzing: {opinion[:50]}...")
    result = call_api(opinion)
    if result:
        result['source_text'] = opinion
        result['index'] = idx
        results.append(result)
        print(f"     ✓ Success - Sentiment: {result.get('sentiment', '?')}")
    else:
        print(f"     ✗ Failed")

print()

print("[3] Saving results...")
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump({
        "total": len(results),
        "success_rate": f"{100*len(results)/len(sample):.0f}%",
        "data": results
    }, f, ensure_ascii=False, indent=2)
print(f"[OK] {OUTPUT_FILE}\n")

print("=" * 70)
print(f"[RESULT] {len(results)}/{len(sample)} successful ({100*len(results)/len(sample):.0f}%)")
print("=" * 70)
