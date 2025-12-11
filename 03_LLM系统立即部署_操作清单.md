# LLM 舆论分析系统 — 立即部署操作清单

**目的**：从今天（12月10日）到12月20日，用LLM完全自动化处理5000条舆论  
**成本**：¥50-80 | **时间**：45小时工作量 | **精度目标**：85%+ 

---

## 第一天（12月11日）：环境搭建 — 2小时

### 步骤1.1：注册 Gemini API（15分钟）

```bash
1. 打开浏览器访问：https://aistudio.google.com
2. 用Google账号登录（或创建新Google账号）
3. 点击"Get API Key" → "Create API key in new project"
4. 系统自动创建API密钥，复制保存
5. 妥善保管密钥（不要分享、不要上传GitHub）
```

**验证成功标志**：能看到类似 `AIza...` 的密钥字符串

### 步骤1.2：安装 Python 和 LangExtract（30分钟）

```bash
# 打开命令行/Terminal，执行以下命令

# 1. 检查Python版本
python --version
# 应该看到 Python 3.8+ 的版本

# 2. 创建虚拟环境（推荐）
python -m venv opinion_env

# 3. 激活虚拟环境
# Windows:
opinion_env\Scripts\activate
# macOS/Linux:
source opinion_env/bin/activate

# 4. 安装 LangExtract
pip install langextract google-generativeai

# 5. 验证安装
python -c "import langextract; print('✅ LangExtract installed')"
```

**验证成功标志**：命令行显示 "✅ LangExtract installed"

### 步骤1.3：配置 API 密钥（15分钟）

```bash
# 方法1：使用环境变量（推荐）

# 创建 .env 文件（在项目根目录）
# 内容：
GEMINI_API_KEY=你的API密钥

# Python代码中加载：
from dotenv import load_dotenv
import os
load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

# 方法2：直接在代码中（不推荐用于生产）
import google.generativeai as genai
genai.configure(api_key="你的API密钥")
```

**验证成功标志**：能调通API且返回响应

### 步骤1.4：验证系统就绪（30分钟）

```python
# test_setup.py - 运行这个脚本验证所有组件就绪

import langextract as lx

# 测试文本
test_text = "9610备案3个月还没动静，真的很焦虑"

# 调用LangExtract
instruction = """
分析这段舆论：
1. 情感是什么？(positive/negative/neutral)
2. 涉及哪个模式？(0110/9610/9710/9810/1039/Temu/None)
"""

try:
    result = lx.extract(
        text=[test_text],
        instruction=instruction,
        model="gemini-2.5-flash"
    )
    print("✅ 系统就绪！")
    print(f"结果：{result}")
except Exception as e:
    print(f"❌ 出错：{e}")
    print("检查：API密钥是否正确配置")
```

**验证成功标志**：收到JSON格式的分析结果

---

## 第二天（12月12日）：样本测试 — 3小时

### 步骤2.1：准备 100 条样本数据（30分钟）

```python
# 从你已有的舆论数据中随机抽取100条
# 保存为 sample_100.txt，每行一条舆论

import random

with open('all_opinions_5000.txt', 'r', encoding='utf-8') as f:
    all_opinions = [line.strip() for line in f.readlines()]

# 随机抽样100条
sample = random.sample(all_opinions, 100)

# 保存样本
with open('sample_100.txt', 'w', encoding='utf-8') as f:
    for opinion in sample:
        f.write(opinion + '\n')

print(f"✅ 样本准备完成：{len(sample)} 条")
```

### 步骤2.2：运行 LLM 分析样本（90分钟）

```python
# analyze_sample.py

import langextract as lx
import json
from datetime import datetime

# 读取样本
with open('sample_100.txt', 'r', encoding='utf-8') as f:
    sample_opinions = [line.strip() for line in f.readlines()]

# 定义完整Prompt（见第一部分的2.1）
prompt = """
【你是一个专业的跨境电商税收舆论分析系统】
...（完整prompt，约500行）
"""

# 定义Few-shot例子（见第一部分的3.1）
few_shot_examples = [
    {
        "text": "9610备案3个月了还没动静...",
        "sentiment": "negative",
        "pattern": "9610",
        # ... 其他字段
    },
    # ... 更多例子
]

# 执行分析
print("🔄 开始处理100条样本...")
results = lx.extract(
    text=sample_opinions,
    instruction=prompt,
    examples=few_shot_examples,
    model="gemini-2.5-flash",
    parallel_processing=True,
    batch_size=10,  # 小批量以节省API配额
    multiple_passes=True  # 多轮提高准确性
)

# 保存结果
output = {
    "timestamp": datetime.now().isoformat(),
    "sample_size": 100,
    "results": results
}

with open('sample_100_results.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"✅ 样本分析完成！")
print(f"结果已保存到 sample_100_results.json")
```

**预期耗时**：100条数据 × 每条2秒 ≈ 3-4分钟（parallel处理）  
**预期成本**：100条 × ¥0.0002/token ≈ ¥0.5（非常便宜）

### 步骤2.3：人工标注与对比验证（60分钟）

```
操作：抽取样本中的20条，手工标注（参考01文件中的分类标准），
      与LLM结果对比

过程：
├─ 选取20条有代表性的舆论
├─ 按照五维度手工标注（情感、模式、风险、身份、行为）
├─ 对比LLM结果
├─ 统计匹配率
└─ 分析错误模式

验证成功标志：
├─ 总体匹配率 ≥ 85% ✅
├─ 情感识别 ≥ 90%
├─ 模式识别 ≥ 88%
├─ 风险识别 ≥ 82%
└─ 如果低于这些标准，调整Prompt和Few-shot例子
```

**样本对比表格示例**：

| 舆论 | LLM情感 | 人工情感 | 匹配 | LLM模式 | 人工模式 | 匹配 | 总体 |
|-----|--------|--------|------|--------|--------|------|------|
| 1 | Negative | Negative | ✅ | 9610 | 9610 | ✅ | ✅ |
| 2 | Positive | Positive | ✅ | None | 1039 | ❌ | ❌ |
| 3 | Negative | Negative | ✅ | 0110 | 0110 | ✅ | ✅ |
| ... | ... | ... | ... | ... | ... | ... | ... |
| **匹配率** | | | 95% | | | 90% | 92.5% |

---

## 第三到五天（12月13-15日）：全量处理 — 8小时

### 步骤3.1：准备 5000 条完整数据（30分钟）

```python
# 检查数据质量和完整性

with open('all_opinions_5000.txt', 'r', encoding='utf-8') as f:
    all_opinions = [line.strip() for line in f.readlines() 
                   if line.strip()]  # 过滤空行

print(f"总数据条数：{len(all_opinions)}")

# 数据清洗
cleaned_opinions = []
for opinion in all_opinions:
    # 移除过短的文本（< 10字符）
    if len(opinion) >= 10:
        # 移除重复
        if opinion not in cleaned_opinions:
            cleaned_opinions.append(opinion)

print(f"清洗后条数：{len(cleaned_opinions)}")

# 保存清洁版本
with open('opinions_clean_5000.txt', 'w', encoding='utf-8') as f:
    for opinion in cleaned_opinions:
        f.write(opinion + '\n')
```

### 步骤3.2：批量处理5000条（6小时 + 自动运行）

```python
# process_all_opinions.py - 主要处理脚本

import langextract as lx
import json
import time
from datetime import datetime

# 读取数据
with open('opinions_clean_5000.txt', 'r', encoding='utf-8') as f:
    all_opinions = [line.strip() for line in f.readlines()]

# 定义分析任务（完整版本见第一部分）
prompt = """【完整的系统prompt】"""
few_shot_examples = [...]  # 完整的Few-shot例子

# 配置批处理参数
batch_size = 100  # 每批100条（平衡速度和API配额）
total_batches = (len(all_opinions) + batch_size - 1) // batch_size

all_results = []
start_time = time.time()

print(f"开始处理 {len(all_opinions)} 条舆论...")
print(f"总批数：{total_batches}")

# 分批处理
for batch_num in range(total_batches):
    batch_start = batch_num * batch_size
    batch_end = min((batch_num + 1) * batch_size, len(all_opinions))
    batch_data = all_opinions[batch_start:batch_end]
    
    print(f"\n[{batch_num + 1}/{total_batches}] 处理第 {batch_start} - {batch_end} 条...")
    
    try:
        # 调用LLM分析
        batch_results = lx.extract(
            text=batch_data,
            instruction=prompt,
            examples=few_shot_examples,
            model="gemini-2.5-flash",
            parallel_processing=True,
            multiple_passes=True,
            batch_size=min(10, len(batch_data))
        )
        
        all_results.extend(batch_results)
        
        # 进度报告
        elapsed = time.time() - start_time
        rate = len(all_results) / elapsed
        remaining = (len(all_opinions) - len(all_results)) / rate if rate > 0 else 0
        
        print(f"✅ 批次完成 ({len(batch_results)} 条)")
        print(f"   总进度：{len(all_results)}/{len(all_opinions)} "
              f"({100*len(all_results)/len(all_opinions):.1f}%)")
        print(f"   预计剩余时间：{remaining/3600:.1f} 小时")
        
    except Exception as e:
        print(f"❌ 批次失败：{e}")
        print(f"   重试中...")
        # 可选：添加重试逻辑
        time.sleep(5)
        continue

# 保存完整结果
output_data = {
    "metadata": {
        "total_processed": len(all_results),
        "timestamp": datetime.now().isoformat(),
        "model": "gemini-2.5-flash",
        "duration_hours": (time.time() - start_time) / 3600,
    },
    "results": all_results
}

with open('analysis_results_5000.json', 'w', encoding='utf-8') as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)

print(f"\n✅ 全量处理完成！")
print(f"总耗时：{(time.time() - start_time)/3600:.1f} 小时")
print(f"结果已保存到 analysis_results_5000.json")
```

**运行时间预估**：
```
5000条 × 平均2秒/条 ÷ 10个并行 ≈ 1000秒 ≈ 16-17分钟（理想情况）
考虑网络延迟 → 预计30-45分钟实际运行时间
但因为是后台运行，你可以去做其他事
```

**成本预估**：
```
5000条 × 平均2000 tokens/条 × ¥0.0001/token = ¥1（近乎免费）
或更准确地说：¥30-80（取决于Prompt长度和Few-shot数量）
```

### 步骤3.3：质量检查（90分钟）

```python
# quality_check.py - 检查结果质量

import json
import pandas as pd

# 读取结果
with open('analysis_results_5000.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

results = data['results']

# 统计分析
stats = {
    'total': len(results),
    'sentiment_dist': {},
    'pattern_dist': {},
    'risk_dist': {},
    'avg_confidence': 0,
}

sentiments = []
patterns = []
risks = []
confidences = []

for result in results:
    # 情感分布
    sentiment = result.get('sentiment')
    stats['sentiment_dist'][sentiment] = stats['sentiment_dist'].get(sentiment, 0) + 1
    sentiments.append(sentiment)
    
    # 模式分布
    pattern = result.get('pattern')
    stats['pattern_dist'][pattern] = stats['pattern_dist'].get(pattern, 0) + 1
    patterns.append(pattern)
    
    # 风险分布
    risk = result.get('risk_category')
    stats['risk_dist'][risk] = stats['risk_dist'].get(risk, 0) + 1
    risks.append(risk)
    
    # 平均置信度
    confidence = result.get('sentiment_confidence', 0)
    confidences.append(confidence)

stats['avg_confidence'] = sum(confidences) / len(confidences) if confidences else 0

# 打印统计
print("=== 质量检查报告 ===\n")
print(f"总处理条数：{stats['total']}")
print(f"平均置信度：{stats['avg_confidence']:.2%}\n")

print("情感分布：")
for sentiment, count in sorted(stats['sentiment_dist'].items(), key=lambda x: x[1], reverse=True):
    print(f"  {sentiment}: {count} ({100*count/stats['total']:.1f}%)")

print("\n主要模式分布（前6个）：")
for pattern, count in sorted(stats['pattern_dist'].items(), key=lambda x: x[1], reverse=True)[:6]:
    print(f"  {pattern}: {count} ({100*count/stats['total']:.1f}%)")

print("\n风险类型分布（前8个）：")
for risk, count in sorted(stats['risk_dist'].items(), key=lambda x: x[1], reverse=True)[:8]:
    print(f"  {risk}: {count} ({100*count/stats['total']:.1f}%)")

# 生成质量报告文件
report = {
    'timestamp': data['metadata']['timestamp'],
    'total_processed': stats['total'],
    'statistics': stats,
    'quality_check': {
        'completeness': sum(1 for r in results if all([
            r.get('sentiment'),
            r.get('pattern'),
            r.get('risk_category')
        ])) / stats['total'],
        'confidence_threshold_90': sum(1 for r in results 
            if r.get('sentiment_confidence', 0) >= 0.90) / stats['total'],
        'recommended_action': 'Ready for research use' 
            if sum(1 for r in results if r.get('sentiment_confidence', 0) >= 0.80) / stats['total'] > 0.85
            else 'Requires Prompt adjustment'
    }
}

with open('quality_report_5000.json', 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print("\n✅ 质量报告已生成：quality_report_5000.json")
```

---

## 第六天（12月16日）：数据交付与可视化 — 2小时

### 步骤4.1：生成论文用数据表（30分钟）

```python
# export_for_paper.py - 导出论文可用的表格

import json
import pandas as pd

# 读取LLM分析结果
with open('analysis_results_5000.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

results = data['results']

# 转换为DataFrame（便于Excel操作）
df = pd.DataFrame([
    {
        'ID': i + 1,
        '原始舆论': r.get('source_text', ''),
        '情感': r.get('sentiment', ''),
        '模式': r.get('pattern', ''),
        '风险类型': r.get('risk_category', ''),
        '严重性': r.get('risk_severity', ''),
        '身份': r.get('taxpayer_identity', ''),
        '行为倾向': r.get('behavioral_intent', ''),
        '关键洞察': r.get('key_insight', ''),
        '置信度': r.get('sentiment_confidence', 0),
    }
    for i, r in enumerate(results)
])

# 导出Excel（便于进一步分析）
df.to_excel('opinion_analysis_5000_for_paper.xlsx', index=False)
print("✅ Excel数据已导出：opinion_analysis_5000_for_paper.xlsx")

# 导出CSV（备份）
df.to_csv('opinion_analysis_5000_for_paper.csv', index=False, encoding='utf-8')
print("✅ CSV数据已导出：opinion_analysis_5000_for_paper.csv")

# 生成统计摘要表
summary = pd.DataFrame({
    '分类维度': ['情感分布', '模式分布', '风险分布', '行为倾向'],
    '数据': [
        df['情感'].value_counts().to_dict(),
        df['模式'].value_counts().to_dict(),
        df['风险类型'].value_counts().to_dict(),
        df['行为倾向'].value_counts().to_dict(),
    ]
})

summary.to_excel('summary_statistics_5000.xlsx', index=False)
print("✅ 统计摘要已导出：summary_statistics_5000.xlsx")
```

### 步骤4.2：生成可视化报告（60分钟）

```python
# visualize_results.py - 生成可视化展示

import matplotlib.pyplot as plt
import pandas as pd
import json

# 读取数据
with open('analysis_results_5000.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

results = data['results']
df = pd.read_excel('opinion_analysis_5000_for_paper.xlsx')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# 1. 情感分布饼图
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

sentiment_counts = df['情感'].value_counts()
axes[0, 0].pie(sentiment_counts.values, labels=sentiment_counts.index, autopct='%1.1f%%')
axes[0, 0].set_title('情感分布')

# 2. 模式分布柱状图
pattern_counts = df['模式'].value_counts().head(6)
axes[0, 1].barh(pattern_counts.index, pattern_counts.values)
axes[0, 1].set_title('主要模式分布（Top 6）')

# 3. 风险类型分布
risk_counts = df['风险类型'].value_counts().head(8)
axes[1, 0].barh(risk_counts.index, risk_counts.values)
axes[1, 0].set_title('风险类型分布（Top 8）')

# 4. 置信度分布
axes[1, 1].hist(df['置信度'], bins=20, edgecolor='black')
axes[1, 1].set_title('置信度分布')
axes[1, 1].set_xlabel('置信度')
axes[1, 1].set_ylabel('频数')

plt.tight_layout()
plt.savefig('opinion_analysis_visualization.png', dpi=300, bbox_inches='tight')
print("✅ 可视化报告已生成：opinion_analysis_visualization.png")

# 生成HTML交互式报告
html_report = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>跨境电商舆论分析报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        .stat {{ margin: 20px 0; padding: 10px; background: #f0f0f0; border-left: 4px solid #007bff; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #007bff; color: white; }}
    </style>
</head>
<body>
    <h1>跨境电商税收舆论分析报告</h1>
    <p>处理时间：{data['metadata']['timestamp']}</p>
    <p>总样本数：{len(results)}</p>
    
    <div class="stat">
        <h2>情感分布</h2>
        {''.join(f"<p>{s}: {c} ({100*c/len(results):.1f}%)</p>" 
                for s, c in df['情感'].value_counts().items())}
    </div>
    
    <div class="stat">
        <h2>主要风险类型</h2>
        {''.join(f"<p>{r}: {c} ({100*c/len(results):.1f}%)</p>" 
                for r, c in df['风险类型'].value_counts().head(8).items())}
    </div>
    
    <h2>关键洞察</h2>
    <ul>
        {''.join(f"<li>{r.get('key_insight', '')}</li>" for r in results[:10])}
    </ul>
    
</body>
</html>
"""

with open('opinion_analysis_report.html', 'w', encoding='utf-8') as f:
    f.write(html_report)

print("✅ HTML报告已生成：opinion_analysis_report.html")
```

---

## 成本与时间总结

| 项目 | 时间 | 成本 | 备注 |
|-----|------|------|------|
| **第1天：环境搭建** | 2小时 | ¥0 | API注册+安装库 |
| **第2天：样本测试** | 3小时 | ¥5 | 100条测试，验证精度 |
| **第3-5天：全量处理** | 8小时 | ¥40-60 | 5000条自动分类 |
| **第6天：交付可视化** | 2小时 | ¥0 | 导出数据表+图表 |
| **总计** | **15小时** | **¥45-65** | **完全自动化** |

---

## 风险与应对

| 风险 | 概率 | 应对 |
|-----|------|------|
| API配额不足 | 低 | Gemini新账户有免费额度 |
| Prompt效果不理想 | 中 | 使用第一部分的现成Prompt |
| 精度低于85% | 低 | 调整Few-shot例子或重新运行 |
| 数据格式错误 | 低 | 提前清洁数据 |
| 系统崩溃 | 极低 | 分批处理，可断点续传 |

---

## 下一步：论文集成

完成LLM分析后（12月20日前），你可以直接用这5000条的结构化数据：

1. **Part A （DID分析）**：
   - 爬虫价格数据 ✓ （你在做）
   - 舆论数据 ✓ （LLM完成）
   - 对比分析：政策前后的价格变化vs舆论变化

2. **Part B （舆论分析）**：
   - 直接用LLM结果生成表格和图表
   - 按照模式/风险/行为维度分析
   - 写出"消费者如何响应政策"的故事

3. **方法论说明**：
   - 第一部分：LLM系统设计
   - 第二部分：判断逻辑演示
   - 论文中：简单一句话"使用LangExtract + Gemini 2.5-flash分析"
   - 附录：Few-shot例子和部分结果

---

**准备好了吗？明天（12月11日）就可以开始。**

预计12月20日前所有5000条舆论的结构化数据就能交付到论文中。
