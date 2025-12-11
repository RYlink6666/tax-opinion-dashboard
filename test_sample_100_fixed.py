#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
样本测试脚本 - 测试100条舆论，验证LLM分析质量 (改进版，显示详细进度)
"""

import json
import sys
import time
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
    except Exception:
        return None

def main():
    print("=" * 70)
    print("[START] Sample Test (100 opinions) - IMPROVED")
    print("=" * 70)
    print()
    
    # 加载
    print("[1] Loading opinions...")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        all_opinions = [line.strip() for line in f if line.strip()]
    
    sample = all_opinions[:SAMPLE_SIZE]
    print(f"[OK] Loaded {len(sample)} opinions\n")
    
    # 分析
    print("[2] Analyzing sample...")
    print(f"[INFO] This will take approximately {SAMPLE_SIZE * 2 // 60}-{SAMPLE_SIZE * 3 // 60} minutes\n")
    
    results = []
    failed = 0
    start_time = time.time()
    
    for idx, opinion in enumerate(sample, 1):
        # 调用API
        result = call_api(opinion)
        
        if result:
            result['source_text'] = opinion
            result['index'] = idx
            results.append(result)
            status = f"✓ {result.get('sentiment', '?')}"
        else:
            failed += 1
            status = "✗ FAILED"
        
        # 进度显示 - 每条显示一次
        elapsed = time.time() - start_time
        rate = idx / elapsed if elapsed > 0 else 0
        remaining = (len(sample) - idx) / rate if rate > 0 else 0
        
        print(f"[{idx:3d}/{SAMPLE_SIZE}] {status:15} | "
              f"Success: {len(results):3d} | Failed: {failed:2d} | "
              f"Elapsed: {int(elapsed):3d}s | "
              f"Est. remaining: {int(remaining):3d}s")
    
    print()
    elapsed_total = time.time() - start_time
    
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
    print(f"Success rate: {100*len(results)/len(sample):.1f}%")
    print(f"Total time: {int(elapsed_total)}s ({int(elapsed_total/60)}m {int(elapsed_total%60)}s)")
    print(f"Average per opinion: {elapsed_total/len(sample):.1f}s\n")
    
    if results:
        # 情感分布
        sentiments = {}
        confidences = []
        for r in results:
            s = r.get('sentiment', 'unknown')
            sentiments[s] = sentiments.get(s, 0) + 1
            confidences.append(r.get('sentiment_confidence', 0))
        
        print("[SENTIMENT] Distribution:")
        for s, c in sorted(sentiments.items()):
            print(f"  {s}: {c} ({100*c/len(results):.0f}%)")
        
        # 置信度
        avg_conf = sum(confidences) / len(confidences) if confidences else 0
        print(f"\n[CONFIDENCE] Sentiment avg: {avg_conf:.2f}")
        
        # 质量判断
        if len(results) >= 85 and avg_conf >= 0.80:
            print("\n✓ QUALITY CHECK PASSED")
            print("  - Success rate ≥ 85% ✓")
            print(f"  - Average confidence ≥ 0.80 ✓")
        else:
            print("\n✗ QUALITY CHECK FAILED")
            if len(results) < 85:
                print(f"  - Success rate {100*len(results)/len(sample):.1f}% < 85%")
            if avg_conf < 0.80:
                print(f"  - Average confidence {avg_conf:.2f} < 0.80")
        
        # 样本
        print("\n[SAMPLE] First 3 results:")
        for i, r in enumerate(results[:3], 1):
            print(f"\n  [{i}] {r.get('brief_summary', 'N/A')}")
            print(f"      Sentiment: {r.get('sentiment')} ({r.get('sentiment_confidence', 0):.2f})")
            print(f"      Topic: {r.get('topic')}")
            print(f"      Actor: {r.get('actor')}")
    
    print("\n" + "=" * 70)
    print("[OK] Sample test complete!")
    print(f"\nNext steps:")
    if len(results) >= 85 and avg_conf >= 0.80:
        print(f"  1. Quality passed! Ready for full analysis")
        print(f"  2. Run: python llm_analyze.py")
    else:
        print(f"  1. Review failed analyses")
        print(f"  2. Adjust system prompt if needed")
    
    return len(results) >= 85 and avg_conf >= 0.80

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
