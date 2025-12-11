#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单API测试
"""

import json
import sys
import io

# 处理Windows编码
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

API_KEY = "57f5636a5d984e18b983ba0e542f3aa4.Ib9C6j2zKNnXvLAm"
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

test_opinion = "跨境电商商品可能会被征税，这会导致商品价格上升，消费者的购买力会下降。"

print("[1] Testing Zhipu API...")
print(f"API_KEY: {API_KEY[:20]}...")
print(f"Model: {MODEL}")
print(f"Test opinion: {test_opinion}\n")

try:
    from zhipuai import ZhipuAI
    print("[OK] zhipuai imported successfully\n")
    
    client = ZhipuAI(api_key=API_KEY)
    print("[OK] ZhipuAI client created\n")
    
    print("[2] Calling API...")
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"分析：{test_opinion}"}
        ],
        temperature=0.3,
        top_p=0.8,
    )
    
    print("[OK] API response received\n")
    
    result_text = response.choices[0].message.content
    print(f"[RAW] {result_text}\n")
    
    # 提取JSON (可能被markdown代码块包装)
    if result_text.startswith("```"):
        # 提取```和```之间的内容
        start = result_text.find('\n') + 1
        end = result_text.rfind('```')
        result_text = result_text[start:end].strip()
    
    result = json.loads(result_text)
    print("[OK] JSON parsed successfully\n")
    
    print("[RESULT]")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
except ImportError as e:
    print(f"[ERR] Import error: {e}")
except json.JSONDecodeError as e:
    print(f"[ERR] JSON decode error: {e}")
    print(f"[RAW] {result_text}")
except Exception as e:
    print(f"[ERR] {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
