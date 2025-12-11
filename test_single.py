#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试单条意见"""

import json
import sys
import time

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

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

test_text = "跨境电商商品可能会被征税，这会导致商品价格上升，消费者的购买力会下降。"

print("[1] Testing API connection...")
print(f"Text: {test_text}\n")

try:
    from zhipuai import ZhipuAI
    print("[OK] zhipuai imported\n")
    
    print("[2] Creating client...")
    client = ZhipuAI(api_key=API_KEY)
    print("[OK] Client created\n")
    
    print("[3] Calling API (this may take 5-10 seconds)...")
    start = time.time()
    
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"分析：{test_text}"}
        ],
        temperature=0.3,
        top_p=0.8,
    )
    
    elapsed = time.time() - start
    print(f"[OK] Response received in {elapsed:.1f}s\n")
    
    result_text = response.choices[0].message.content
    print(f"[RAW] {result_text[:200]}...\n")
    
    # 提取JSON
    if result_text.startswith("```"):
        start = result_text.find('\n') + 1
        end = result_text.rfind('```')
        result_text = result_text[start:end].strip()
    
    print("[4] Parsing JSON...")
    result = json.loads(result_text)
    print("[OK] JSON parsed successfully\n")
    
    print("[RESULT]")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    print("\n✓ API works correctly!")
    
except Exception as e:
    print(f"✗ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
