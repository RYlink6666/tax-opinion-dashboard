#!/usr/bin/env python3
"""
半自动化数据分析脚本
功能：
1. 读取原始意见数据
2. 检查已分析 vs 未分析
3. 对新数据调用Zhipu AI LLM进行分析
4. 合并结果到analysis_results.json
5. 自动推送到GitHub
6. 输出成本统计

使用方法：
    python auto_analyze.py
"""

import json
import os
import subprocess
import time
from pathlib import Path
from datetime import datetime
import sys

# 配置
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
CLEAN_DATA_FILE = DATA_DIR / "clean" / "opinions_clean_5000.json"
ANALYSIS_FILE = DATA_DIR / "analysis" / "analysis_results.json"
ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY")  # 从环境变量读取

def load_clean_opinions():
    """加载已清理的原始意见"""
    print("📥 加载原始意见数据...")
    with open(CLEAN_DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    opinions = data if isinstance(data, list) else data.get('data', [])
    print(f"   ✓ 加载了 {len(opinions)} 条意见")
    return opinions

def load_analyzed_results():
    """加载已分析的结果"""
    print("📋 加载已分析结果...")
    if ANALYSIS_FILE.exists():
        with open(ANALYSIS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        results = data.get('data', [])
        print(f"   ✓ 加载了 {len(results)} 条分析结果")
        return results
    else:
        print("   ℹ️ 还没有分析结果文件，将创建新文件")
        return []

def find_new_opinions(clean_opinions, analyzed_results):
    """找出未分析的意见"""
    print("🔍 检查未分析的意见...")
    
    # 已分析的source_text集合
    analyzed_texts = {r.get('source_text') for r in analyzed_results if r.get('source_text')}
    
    # 找出未分析的意见
    # clean_opinions中的每条是字典，包含'content'字段
    new_opinions = []
    for op in clean_opinions:
        # 提取content
        content = op.get('content') if isinstance(op, dict) else op
        if content and content not in analyzed_texts:
            new_opinions.append(op)
    
    analyzed_count = len(analyzed_results)
    new_count = len(new_opinions)
    total_count = len(clean_opinions)
    
    print(f"   已分析: {analyzed_count} 条")
    print(f"   未分析: {new_count} 条")
    print(f"   总计: {total_count} 条")
    print(f"   覆盖率: {analyzed_count/total_count*100:.1f}%")
    
    return new_opinions

def call_zhipu_api_single(opinion_text, api_key):
    """调用单条Zhipu API"""
    try:
        from zhipuai import ZhipuAI
    except ImportError:
        print("   ⚠️  zhipuai not installed. Run: pip install zhipuai")
        return None
    
    system_prompt = """你是一个专业的跨境电商税收舆论分析系统。请对用户提供的舆论进行以下5个维度的结构化分析，并以JSON格式返回结果。

分析维度：
1. **sentiment（情感倾向）** - 值: "positive"、"neutral"、"negative"，置信度: 0-1
2. **topic（核心话题）** - 值: "tax_policy"、"price_impact"、"compliance"、"business_risk"、"advocacy"、"other"，置信度: 0-1
3. **pattern（模式分类）** - 值: "0110"、"9610"、"9710"、"9810"、"1039"、"Temu"、"multiple"、"unknown"，置信度: 0-1
4. **risk_level（风险程度）** - 值: "critical"、"high"、"medium"、"low"，置信度: 0-1
5. **actor（参与方）** - 值: "enterprise"、"consumer"、"government"、"cross_border_seller"、"general_public"、"multiple"，置信度: 0-1

**返回格式（必须是有效的JSON）：**
{"sentiment": "...", "sentiment_confidence": 0.85, "topic": "...", "topic_confidence": 0.90, "pattern": "...", "pattern_confidence": 0.75, "risk_level": "...", "risk_confidence": 0.88, "actor": "...", "actor_confidence": 0.80, "key_phrase": "...", "brief_summary": "..."}"""
    
    try:
        client = ZhipuAI(api_key=api_key)
        response = client.chat.completions.create(
            model="glm-4-flash",
            messages=[
                {"role": "system", "content": system_prompt},
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
        result = json.loads(result_text)
        return result
            
    except Exception as e:
        return None

def analyze_with_zhipu(opinions_batch):
    """
    使用Zhipu AI进行批量分析
    """
    print(f"\n🤖 调用Zhipu AI分析 {len(opinions_batch)} 条意见...")
    
    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        # 如果环境变量不存在，使用hardcoded的key（需要替换为实际密钥）
        api_key = "91cff4bec1fe4bdfa2cb35fc5ca03002.YngoEUjQqKF0f6qN"
        if not api_key or api_key.startswith("your"):
            print("   ⚠️  未设置ZHIPU_API_KEY环境变量或硬编码密钥")
            print("   请运行: set ZHIPU_API_KEY=<your-api-key>")
            return [], 0
    
    analyzed = []
    cost = 0  # 简化处理，不计算精确成本
    
    for idx, opinion in enumerate(opinions_batch, 1):
        # 从opinion中提取content（如果是字典）
        opinion_text = opinion.get('content') if isinstance(opinion, dict) else opinion
        
        result = call_zhipu_api_single(opinion_text, api_key)
        
        if result:
            result['source_text'] = opinion_text
            analyzed.append(result)
            status = "✓"
        else:
            status = "✗"
        
        # 进度显示
        if idx % 10 == 0:
            print(f"   [{idx:4d}/{len(opinions_batch)}] {status}")
            
        # 避免超限：每50条休息3秒
        if idx % 50 == 0:
            time.sleep(3)
    
    print(f"   ✓ 完成 {len(analyzed)}/{len(opinions_batch)}")
    return analyzed, cost

def merge_results(old_results, new_analyzed):
    """合并旧结果和新分析结果"""
    print("\n📊 合并分析结果...")
    merged = old_results + new_analyzed
    print(f"   ✓ 总共 {len(merged)} 条分析结果")
    return merged

def save_results(results):
    """保存结果到JSON"""
    print("💾 保存结果到文件...")
    
    # 确保目录存在
    ANALYSIS_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    output_data = {
        'total': len(results),
        'model': 'glm-4-flash',
        'api_key_prefix': '91cff4bec1',
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
        message = f"Auto: 更新分析数据 ({timestamp})"
        subprocess.run(['git', 'commit', '-m', message], check=True)
        print("   ✓ git commit")
        
        # git push
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)
        print("   ✓ git push")
        print("   ✓ Streamlit将在几分钟后自动重新部署")
        
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Git操作失败: {e}")
        print("   可能原因: 网络问题 或 没有新的提交")
        return False
    
    return True

def print_summary(analyzed_count, total_cost):
    """打印总结"""
    print("\n" + "="*60)
    print("📊 分析总结")
    print("="*60)
    print(f"本次新分析: {analyzed_count} 条意见")
    print(f"API成本: ¥ {total_cost:.2f}")
    print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    print("\n✨ 数据已更新！")
    print("访问网站查看最新分析：https://tax-opinion-dashboard-atbvxazynv7jcjpsjhdvzh.streamlit.app/")

def main():
    """主流程"""
    print("\n" + "="*60)
    print("🚀 跨境电商税收政策舆论分析系统 - 自动更新脚本")
    print("="*60)
    
    try:
        # 1. 加载数据
        clean_opinions = load_clean_opinions()
        analyzed_results = load_analyzed_results()
        
        # 2. 检查未分析意见
        new_opinions = find_new_opinions(clean_opinions, analyzed_results)
        
        if len(new_opinions) == 0:
            print("\n✅ 所有意见都已分析，无需更新")
            return
        
        # 3. 分析新意见
        print(f"\n⏳ 开始分析 {len(new_opinions)} 条未分析意见...")
        new_analyzed, cost = analyze_with_zhipu(new_opinions)
        
        if len(new_analyzed) == 0:
            print("\n⚠️  分析未完成（API调用失败或未配置）")
            print("请确保：")
            print("  1. 设置了ZHIPU_API_KEY环境变量")
            print("  2. API密钥有足够的余额")
            return
        
        # 4. 合并结果
        merged_results = merge_results(analyzed_results, new_analyzed)
        
        # 5. 保存结果
        save_results(merged_results)
        
        # 6. 推送到GitHub
        git_success = git_commit_and_push()
        
        # 7. 打印总结
        print_summary(len(new_analyzed), cost)
        
        if git_success:
            print("\n💡 下次更新提示：")
            print("   • 每周一次：cron "0 10 * * 1 python auto_analyze.py"（Linux/Mac）")
            print("   • Windows任务计划：见 SCHEDULE_TASKS.md")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
