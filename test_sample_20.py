#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""快速测试20条"""

import json
import sys
import time
from pathlib import Path

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

INPUT_FILE = Path("data/clean/opinions_clean_5000.txt")
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
        if result_text.startswith("```"):
            start = result_text.find('\n') + 1
            end = result_text.rfind('```')
            result_text = result_text[start:end].strip()
        return json.loads(result_text)
    except Exception:
        return None

print("=" * 60)
print("[TEST] 20 opinions (快速测试)")
print("=" * 60)
print()

with open(INPUT_FILE, 'r', encoding='utf-8') as f:
    opinions = [line.strip() for line in f if line.strip()][:20]

print(f"[1] Loaded {len(opinions)} opinions\n")
print("[2] Analyzing (this takes 1-2 minutes)...\n")

results = []
start_time = time.time()

for idx, opinion in enumerate(opinions, 1):
    result = call_api(opinion)
    if result:
        results.append(result)
        status = "✓"
    else:
        status = "✗"
    
    elapsed = time.time() - start_time
    rate = idx / elapsed if elapsed > 0 else 0
    remaining = (len(opinions) - idx) / rate if rate > 0 else 0
    
    print(f"[{idx:2d}/{len(opinions)}] {status} | Elapsed: {int(elapsed):2d}s | Remaining: ~{int(remaining):2d}s")

elapsed_total = time.time() - start_time
print()
print("=" * 60)
print(f"[RESULT] {len(results)}/{len(opinions)} successful ({100*len(results)/len(opinions):.0f}%)")
print(f"[TIME] Total: {int(elapsed_total)}s")
print("=" * 60)

if results:
    sentiments = {}
    confs = []
    for r in results:
        s = r.get('sentiment', '?')
        sentiments[s] = sentiments.get(s, 0) + 1
        confs.append(r.get('sentiment_confidence', 0))
    
    print(f"\n[SENTIMENT] {sentiments}")
    print(f"[CONFIDENCE] Avg: {sum(confs)/len(confs):.2f}")
    
    if len(results) >= 17 and sum(confs)/len(confs) >= 0.75:
        print("\n✓ Quality OK - ready for 100 sample test")
    else:
        print("\n⚠ Quality needs improvement")
