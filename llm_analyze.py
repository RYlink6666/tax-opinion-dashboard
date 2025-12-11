#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM舆论分析脚本 - 使用智谱清言API进行5维度分析
"""

import json
import sys
import time
from pathlib import Path
from datetime import datetime

# 处理Windows编码问题
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# API配置
API_KEY = "91cff4bec1fe4bdfa2cb35fc5ca03002.YngoEUjQqKF0f6qN"
MODEL = "glm-4-flash"

# 输入输出文件
INPUT_FILE = Path("data/clean/opinions_clean_5000.txt")
OUTPUT_FILE = Path("data/analysis/analysis_results.json")
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

# ============================================================================
# 系统Prompt - 5维度分析
# ============================================================================

SYSTEM_PROMPT = """你是一个专业的跨境电商税收舆论分析系统。请对用户提供的舆论进行以下5个维度的结构化分析，并以JSON格式返回结果。

分析维度：

1. **sentiment（情感倾向）** - 评估舆论的整体情感
   - 值: "positive"（正面）、"neutral"（中立）、"negative"（负面）
   - 置信度: 0-1之间的数字

2. **topic（核心话题）** - 识别舆论主要讨论的话题
   - 值: "tax_policy"（税收政策）、"price_impact"（价格影响）、"compliance"（合规）、
         "business_risk"（商业风险）、"advocacy"（政策倡议）、"other"（其他）
   - 置信度: 0-1之间的数字

3. **pattern（模式分类）** - 舆论对应的跨境电商模式
   - 值: "0110"、"9610"、"9710"、"9810"、"1039"、"Temu"、"multiple"（多个）、"unknown"（不明确）
   - 置信度: 0-1之间的数字

4. **risk_level（风险程度）** - 评估舆论反映的风险程度
   - 值: "critical"（严重）、"high"（高）、"medium"（中等）、"low"（低）
   - 置信度: 0-1之间的数字

5. **actor（参与方）** - 识别舆论中涉及的主要参与方
   - 值: "enterprise"（企业）、"consumer"（消费者）、"government"（政府）、
         "cross_border_seller"（跨境卖家）、"general_public"（大众）、"multiple"（多个）
   - 置信度: 0-1之间的数字

**返回格式（必须是有效的JSON）：**
{
    "sentiment": "positive|neutral|negative",
    "sentiment_confidence": 0.85,
    "topic": "tax_policy|price_impact|compliance|business_risk|advocacy|other",
    "topic_confidence": 0.90,
    "pattern": "0110|9610|9710|9810|1039|Temu|multiple|unknown",
    "pattern_confidence": 0.75,
    "risk_level": "critical|high|medium|low",
    "risk_confidence": 0.88,
    "actor": "enterprise|consumer|government|cross_border_seller|general_public|multiple",
    "actor_confidence": 0.80,
    "key_phrase": "提取的关键短语",
    "brief_summary": "舆论的简短总结（20字以内）"
}

注意：
- 所有置信度必须在0-1之间
- key_phrase应该是舆论中最能代表其观点的短语
- brief_summary应该客观总结舆论的主要内容
- 返回的必须是有效的JSON格式"""

# ============================================================================
# 调用LLM的函数
# ============================================================================

def call_zhipu_api(opinion_text):
    """调用智谱清言API进行分析"""
    try:
        from zhipuai import ZhipuAI
    except ImportError:
        print("[ERR] zhipuai not installed. Run: pip install zhipuai")
        return None
    
    try:
        client = ZhipuAI(api_key=API_KEY)
        
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"分析这条舆论：{opinion_text}"}
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
        
        # 尝试解析JSON
        try:
            result = json.loads(result_text)
            return result
        except json.JSONDecodeError:
            # 如果不是有效JSON，返回None
            return None
            
    except Exception as e:
        print(f"[ERR] API call failed: {e}")
        return None

# ============================================================================
# 主分析流程
# ============================================================================

def load_opinions():
    """加载清洁后的舆论数据"""
    if not INPUT_FILE.exists():
        print(f"[ERR] Input file not found: {INPUT_FILE}")
        return []
    
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        opinions = [line.strip() for line in f if line.strip()]
    
    return opinions

def analyze_opinions(opinions, sample_size=None, start_idx=0):
    """分析舆论"""
    # 跳过前start_idx条
    if start_idx > 0:
        opinions = opinions[start_idx:]
        print(f"[INFO] Skipping first {start_idx} opinions, starting from index {start_idx}\n")
    
    if sample_size and len(opinions) > sample_size:
        opinions = opinions[:sample_size]
    
    results = []
    failed = 0
    
    print(f"[START] Analyzing {len(opinions)} opinions")
    print(f"[API] {MODEL} (Key: {API_KEY[:10]}...)\n")
    
    start_time = time.time()
    
    for idx, opinion in enumerate(opinions, 1):
        # 调用API
        result = call_zhipu_api(opinion)
        
        if result:
            result['source_text'] = opinion
            result['index'] = idx
            results.append(result)
            status = "✓"
        else:
            failed += 1
            status = "✗"
        
        # 进度显示 - 每条显示
        if idx % 5 == 0:  # 每5条显示一次（避免太多输出）
            elapsed = time.time() - start_time
            rate = idx / elapsed if elapsed > 0 else 0
            remaining = (len(opinions) - idx) / rate if rate > 0 else 0
            rate_min = idx / (elapsed / 60) if elapsed > 0 else 0
            
            print(f"[{idx:4d}/{len(opinions)}] {status} | "
                  f"Success: {len(results):4d} | Failed: {failed:3d} | "
                  f"Rate: {rate_min:.1f}/min | "
                  f"ETA: {int(remaining/60)}m {int(remaining%60)}s")
            sys.stdout.flush()  # 实时刷新输出
        
        # 避免超限：每10条休息1秒
        if idx % 10 == 0:
            time.sleep(1)
    
    print(f"\n[OK] Analysis complete")
    print(f"[STATS] Success: {len(results)}, Failed: {failed}, Rate: {100*len(results)/len(opinions):.1f}%\n")
    
    return results

def save_results(results):
    """保存分析结果"""
    print(f"[EXPORT] {OUTPUT_FILE.name}")
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump({
            "total": len(results),
            "model": MODEL,
            "api_key_prefix": API_KEY[:10],
            "data": results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] Saved {len(results)} results\n")

def generate_statistics(results):
    """生成统计报告"""
    print("=" * 70)
    print("[STATS] Analysis summary")
    print("=" * 70)
    
    if not results:
        print("[ERR] No results to analyze")
        return
    
    # 情感分布
    sentiment_count = {}
    for r in results:
        sent = r.get('sentiment', 'unknown')
        sentiment_count[sent] = sentiment_count.get(sent, 0) + 1
    
    print("\n[SENTIMENT] Distribution:")
    for sent, count in sorted(sentiment_count.items()):
        pct = 100 * count / len(results)
        print(f"  {sent}: {count} ({pct:.1f}%)")
    
    # 话题分布
    topic_count = {}
    for r in results:
        topic = r.get('topic', 'unknown')
        topic_count[topic] = topic_count.get(topic, 0) + 1
    
    print("\n[TOPIC] Distribution:")
    for topic, count in sorted(topic_count.items(), key=lambda x: -x[1])[:5]:
        pct = 100 * count / len(results)
        print(f"  {topic}: {count} ({pct:.1f}%)")
    
    # 风险等级
    risk_count = {}
    for r in results:
        risk = r.get('risk_level', 'unknown')
        risk_count[risk] = risk_count.get(risk, 0) + 1
    
    print("\n[RISK] Distribution:")
    for risk, count in sorted(risk_count.items()):
        pct = 100 * count / len(results)
        print(f"  {risk}: {count} ({pct:.1f}%)")
    
    # 平均置信度
    avg_confidence = sum(
        r.get('sentiment_confidence', 0) + 
        r.get('topic_confidence', 0) + 
        r.get('pattern_confidence', 0) + 
        r.get('risk_confidence', 0) + 
        r.get('actor_confidence', 0)
        for r in results
    ) / (len(results) * 5)
    
    print(f"\n[CONFIDENCE] Average: {avg_confidence:.2f}")
    
    print("\n" + "=" * 70)

def main():
    print("=" * 70)
    print("[START] LLM Opinion Analysis (Phase 2)")
    print("=" * 70)
    print()
    
    # 1. 加载舆论
    print("[STEP1] Load cleaned opinions")
    opinions = load_opinions()
    
    if not opinions:
        print("[ERR] No opinions loaded")
        return False
    
    print(f"[OK] Loaded {len(opinions)} opinions\n")
    
    # 2. 分析（先用样本测试，改为full时分析全部）
    print("[STEP2] Analyze opinions")
    SAMPLE_SIZE = None  # 改为 100 进行样本测试，改为 None 进行全量分析
    START_IDX = 900  # 从第900条开始（跳过前900条），改为 0 进行完整分析
    
    results = analyze_opinions(opinions, sample_size=SAMPLE_SIZE, start_idx=START_IDX)
    
    if not results:
        print("[ERR] Analysis failed")
        return False
    
    # 3. 保存结果
    print("[STEP3] Save results")
    save_results(results)
    
    # 4. 生成统计
    print("[STEP4] Generate statistics")
    generate_statistics(results)
    
    print(f"[OK] Analysis complete!")
    print(f"[OUTPUT] {OUTPUT_FILE}")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
