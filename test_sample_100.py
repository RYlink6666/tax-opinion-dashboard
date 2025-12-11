#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
样本测试脚本 - 测试100条舆论，验证LLM分析质量
"""

import json
import sys
from pathlib import Path

# 处理Windows编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ============================================================================
# 配置
# ============================================================================

INPUT_FILE = Path("data/clean/opinions_clean_5000.txt")
OUTPUT_FILE = Path("data/analysis/sample_100_results.json")
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

SAMPLE_SIZE = 100

# API配置
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

# ============================================================================
# 函数
# ============================================================================

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
    except ImportError as e:
        print(f"[ERR] Import failed: {e}")
        return None
    except json.JSONDecodeError as e:
        return None
    except Exception as e:
        # Don't print every error, just fail silently for now
        return None

def main():
    print("=" * 70)
    print("[START] Sample Test (100 opinions)")
    print("=" * 70)
    print()
    
    # 加载
    print("[1] Loading opinions...")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        all_opinions = [line.strip() for line in f if line.strip()]
    
    sample = all_opinions[:SAMPLE_SIZE]
    print(f"[OK] Loaded {len(sample)} opinions for testing\n")
    
    # 分析
    print("[2] Analyzing sample...")
    results = []
    
    for idx, opinion in enumerate(sample, 1):
        if idx % 10 == 0:
            print(f"    [{idx}/{SAMPLE_SIZE}] {len(results)} successful")
        
        result = call_api(opinion)
        if result:
            result['source_text'] = opinion
            result['index'] = idx
            results.append(result)
    
    print(f"    [{SAMPLE_SIZE}/{SAMPLE_SIZE}] Done\n")
    
    # 保存
    print("[3] Saving results...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump({
            "total": len(results),
            "success_rate": f"{100*len(results)/len(sample):.1f}%",
            "data": results
        }, f, ensure_ascii=False, indent=2)
    print(f"[OK] {OUTPUT_FILE}\n")
    
    # 统计
    print("=" * 70)
    print("[STATS] Quality check")
    print("=" * 70)
    print(f"\nTotal analyzed: {len(results)}/{len(sample)}")
    print(f"Success rate: {100*len(results)/len(sample):.1f}%\n")
    
    if results:
        # 情感分布
        sentiments = {}
        for r in results:
            s = r.get('sentiment', 'unknown')
            sentiments[s] = sentiments.get(s, 0) + 1
        
        print("[SENTIMENT] Distribution:")
        for s, c in sentiments.items():
            print(f"  {s}: {c} ({100*c/len(results):.0f}%)")
        
        # 置信度
        avg_conf = sum(r.get('sentiment_confidence', 0) for r in results) / len(results)
        print(f"\n[CONFIDENCE] Sentiment avg: {avg_conf:.2f}")
        
        # 样本
        print("\n[SAMPLE] First 3 results:")
        for i, r in enumerate(results[:3], 1):
            print(f"  [{i}] {r.get('brief_summary', 'N/A')}")
            print(f"      Sentiment: {r.get('sentiment')} ({r.get('sentiment_confidence', 0):.2f})")
            print(f"      Topic: {r.get('topic')}")
            print()
    
    print("=" * 70)
    print("[OK] Sample test complete!")
    print(f"\nNext: If satisfied, run full analysis:")
    print(f"  python llm_analyze.py")
    
    return True

if __name__ == "__main__":
    main()
