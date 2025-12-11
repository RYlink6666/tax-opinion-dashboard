#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析缺失的900条记录 - 禁用代理版本
"""

import json
import os
import sys
import time
import subprocess
from pathlib import Path
from datetime import datetime

# 清除代理环境变量（解决socks4代理冲突）
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
os.environ.pop('ALL_PROXY', None)

# 处理Windows编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ============================================================================
# 配置
# ============================================================================

PROJECT_ROOT = Path(__file__).parent
CLEAN_DATA_FILE = PROJECT_ROOT / "data" / "clean" / "opinions_clean_5000.json"
ANALYSIS_FILE = PROJECT_ROOT / "data" / "analysis" / "analysis_results.json"

# Zhipu API配置
API_KEY = "91cff4bec1fe4bdfa2cb35fc5ca03002.YngoEUjQqKF0f6qN"
MODEL = "glm-4-flash"

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
# 加载数据函数
# ============================================================================

def load_clean_opinions():
    """加载原始干净数据"""
    print("📥 加载原始意见数据...")
    with open(CLEAN_DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    opinions = data.get('data', []) if isinstance(data, dict) else data
    print(f"   ✓ 加载了 {len(opinions)} 条意见")
    return opinions

def load_analyzed_results():
    """加载已分析的结果"""
    print("📋 加载已分析结果...")
    if ANALYSIS_FILE.exists():
        with open(ANALYSIS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        results = data.get('data', []) if isinstance(data, dict) else data
        print(f"   ✓ 加载了 {len(results)} 条分析结果")
        return results
    else:
        print("   ℹ️ 还没有分析结果文件")
        return []

# ============================================================================
# Zhipu API 调用函数
# ============================================================================

def call_zhipu_api(opinion_text, retry_count=3):
    """调用Zhipu API进行分析，带重试机制"""
    try:
        from zhipuai import ZhipuAI
    except ImportError:
        print("   ⚠️  zhipuai not installed. Run: pip install zhipuai")
        return None
    
    for attempt in range(retry_count):
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
            if "```" in result_text:
                start = result_text.find('\n') + 1
                end = result_text.rfind('```')
                result_text = result_text[start:end].strip()
            
            # 尝试解析JSON
            try:
                result = json.loads(result_text)
                return result
            except json.JSONDecodeError as e:
                return None
                
        except Exception as e:
            if attempt < retry_count - 1:
                time.sleep(2)  # 等待后重试
            else:
                return None

# ============================================================================
# 分析缺失记录
# ============================================================================

def find_missing_opinions(clean_opinions, analyzed_results):
    """找出未分析的意见及其索引"""
    print("🔍 检查未分析的意见...")
    
    # 已分析的source_text集合
    analyzed_texts = {r.get('source_text') for r in analyzed_results if r.get('source_text')}
    
    # 找出未分析的意见及其索引
    missing = []
    for idx, op in enumerate(clean_opinions):
        content = op.get('content') if isinstance(op, dict) else op
        if content and content not in analyzed_texts:
            missing.append({'index': idx, 'content': content, 'opinion': op})
    
    print(f"   已分析: {len(analyzed_texts)} 条")
    print(f"   未分析: {len(missing)} 条")
    print(f"   总计: {len(clean_opinions)} 条")
    print(f"   覆盖率: {len(analyzed_texts)/len(clean_opinions)*100:.1f}%")
    
    return missing

def analyze_batch(missing_opinions, batch_size=50):
    """批量分析缺失的意见"""
    print(f"\n🤖 开始分析 {len(missing_opinions)} 条意见...")
    print(f"   ✓ 代理已禁用")
    
    analyzed = []
    failed_indices = []
    total_cost = 0
    
    start_time = time.time()
    
    for idx, item in enumerate(missing_opinions, 1):
        opinion_text = item['content']
        opinion_idx = item['index']
        
        # 调用API
        result = call_zhipu_api(opinion_text)
        
        if result:
            result['source_text'] = opinion_text
            result['index'] = opinion_idx
            analyzed.append(result)
            status = "✓"
        else:
            failed_indices.append(opinion_idx)
            status = "✗"
        
        # 进度显示
        if idx % 10 == 0:
            elapsed = time.time() - start_time
            rate = idx / elapsed if elapsed > 0 else 0
            remaining = (len(missing_opinions) - idx) / rate if rate > 0 else 0
            
            print(f"   [{idx:4d}/{len(missing_opinions)}] {status} | "
                  f"成功: {len(analyzed):4d} | 失败: {len(failed_indices):3d} | "
                  f"速率: {rate:.1f}/min | "
                  f"剩余: {int(remaining/60)}m {int(remaining%60)}s")
            sys.stdout.flush()
        
        # 避免超限：每50条休息5秒
        if idx % 50 == 0:
            print(f"   ⏸️  休息5秒...")
            time.sleep(5)
    
    elapsed_minutes = (time.time() - start_time) / 60
    print(f"\n✅ 分析完成")
    print(f"   成功: {len(analyzed)}/{len(missing_opinions)}")
    print(f"   耗时: {elapsed_minutes:.1f} 分钟")
    
    return analyzed, failed_indices

def merge_results(old_results, new_analyzed):
    """合并旧结果和新分析结果"""
    print("\n📊 合并分析结果...")
    merged = old_results + new_analyzed
    merged_sorted = sorted(merged, key=lambda x: x.get('index', 999999))
    print(f"   ✓ 总共 {len(merged_sorted)} 条分析结果")
    return merged_sorted

def save_results(results):
    """保存结果到JSON"""
    print("💾 保存结果到文件...")
    
    # 确保目录存在
    ANALYSIS_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    output_data = {
        'total': len(results),
        'model': MODEL,
        'api_key_prefix': API_KEY[:10],
        'last_updated': datetime.now().isoformat(),
        'data': results
    }
    
    with open(ANALYSIS_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"   ✓ 保存到 {ANALYSIS_FILE}")

def git_commit_and_push():
    """自动提交和推送到GitHub"""
    print("\n📤 推送到GitHub...")
    
    try:
        os.chdir(PROJECT_ROOT)
        
        # git add
        subprocess.run(['git', 'add', 'data/analysis/analysis_results.json'], check=True)
        print("   ✓ git add")
        
        # git commit
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        message = f"Auto: 分析缺失的900条记录 ({timestamp})"
        subprocess.run(['git', 'commit', '-m', message], check=True)
        print("   ✓ git commit")
        
        # git push
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)
        print("   ✓ git push")
        print("   ✓ Streamlit将在几分钟后自动重新部署")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Git操作失败: {e}")
        return False

# ============================================================================
# 主程序
# ============================================================================

def main():
    print("\n" + "="*60)
    print("🚀 分析缺失的900条记录（禁用代理版本）")
    print("="*60)
    
    try:
        # 1. 加载数据
        clean_opinions = load_clean_opinions()
        analyzed_results = load_analyzed_results()
        
        # 2. 找出缺失的
        missing = find_missing_opinions(clean_opinions, analyzed_results)
        
        if len(missing) == 0:
            print("\n✅ 所有意见都已分析，无需更新")
            return True
        
        # 3. 分析缺失意见
        print(f"\n⏳ 开始分析 {len(missing)} 条未分析意见...")
        new_analyzed, failed = analyze_batch(missing)
        
        if len(new_analyzed) == 0:
            print("\n⚠️  分析未完成")
            return False
        
        # 4. 合并结果
        merged_results = merge_results(analyzed_results, new_analyzed)
        
        # 5. 保存结果
        save_results(merged_results)
        
        # 6. 推送到GitHub
        git_success = git_commit_and_push()
        
        # 7. 打印总结
        print("\n" + "="*60)
        print("📊 分析总结")
        print("="*60)
        print(f"新分析: {len(new_analyzed)} 条意见")
        print(f"分析失败: {len(failed)} 条")
        print(f"总记录数: {len(merged_results)}")
        print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        print("\n✨ 数据已更新！")
        print("访问网站查看最新分析：")
        print("https://tax-opinion-dashboard-atbvxazynv7jcjpsjhdvzh.streamlit.app/")
        
        return git_success
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
