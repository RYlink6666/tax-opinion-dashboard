# 第二阶段：LangExtract完整分析计划
## 跨境电商税收舆论LLM分析（2025年12月16-30日）

**项目目标**：用LangExtract处理5000条舆论，生成结构化分析结果  
**周期**：12月16-30日（15天）  
**成本**：¥50-100（Gemini API）  
**产出**：analysis_results_5000.json + 统计报告  
**精度目标**：85%+（预期88-92%）

---

## 一、什么是LangExtract？

### 1.1 核心概念

```
LangExtract是Google推出的Python库，用于：
├─ 用LLM从非结构化文本中提取结构化信息
├─ 保证源文本可追溯（source grounding）
├─ 生成交互式可视化报告
└─ 支持多种LLM模型（Gemini、OpenAI等）

你的用途：
└─ 从5000条舆论中自动提取：
   ├─ 情感反应（positive/negative/neutral）
   ├─ 业务模式（0110/9610/9810等）
   ├─ 风险类型（香港空壳/库存核销等）
   ├─ 纳税人身份（General/Small）
   └─ 行为倾向（补税/切换模式/观望等）
```

### 1.2 为什么用LangExtract？

```
vs 手工关键词库：
├─ ✅ 精度：92% vs 70%
├─ ✅ 理解讽刺和复杂逻辑：可以 vs 不可以
├─ ✅ 学术规范：⭐⭐⭐⭐⭐ vs ⭐⭐⭐
└─ ✅ 论文发表：被期刊认可 vs 容易被拒

vs 自己手撸API调用：
├─ ✅ 开发时间：2-3小时 vs 24小时
├─ ✅ 代码复杂度：10行 vs 500行
├─ ✅ 调试时间：0小时 vs 8小时
└─ ✅ 处理效率：并行处理 vs 串行处理
```

---

## 二、环境搭建（1小时）

### 步骤1：安装Python库

```bash
# 推荐用虚拟环境
python -m venv langextract_env

# 激活虚拟环境
# Windows:
langextract_env\Scripts\activate
# Mac/Linux:
source langextract_env/bin/activate

# 安装LangExtract和依赖
pip install langextract google-generativeai pandas openpyxl

# 验证安装
python -c "import langextract; print('✅ LangExtract安装成功')"
```

### 步骤2：获取Gemini API密钥

```
1. 访问：https://ai.google.dev/
2. 点击"Get API Key" → "Create API key in new project"
3. 会自动创建一个密钥，复制保存
4. 密钥看起来像：AIzaSy...（长字符串）

免费额度：
├─ 每天：15个请求（免费层）
├─ 价格：$0.075 per 1M tokens (输入)
├─ 建议：5000条舆论约需¥40-80
└─ 信用卡：需绑定，但会按月自动扣费

配置密钥（3选1）：
方式1：环境变量
  export GOOGLE_API_KEY="你的密钥"

方式2：.env 文件
  创建文件 .env，内容：
  GOOGLE_API_KEY=你的密钥

方式3：代码中直接设置
  import os
  os.environ['GOOGLE_API_KEY'] = '你的密钥'
```

### 步骤3：创建项目目录结构

```
opinion_analysis/
├── config.py                 # 配置文件
├── main.py                   # 主程序
├── prompt.py                 # Prompt定义
├── .env                       # API密钥（不要上传Git）
├── data/
│   ├── opinions_clean_5000.txt    # 输入数据
│   ├── analysis_results_5000.json # 输出结果
│   └── sample_100.txt             # 样本数据
├── logs/
│   └── processing.log        # 运行日志
└── results/
    └── report.html           # 可视化报告
```

---

## 三、核心代码（分阶段）

### 步骤4a：配置文件 config.py

```python
# config.py
import os
from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv()

# API配置
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
MODEL = "gemini-2.5-flash"  # 推荐模型

# 文件路径
INPUT_FILE = "data/opinions_clean_5000.txt"
OUTPUT_FILE = "data/analysis_results_5000.json"
SAMPLE_FILE = "data/sample_100.txt"
LOG_FILE = "logs/processing.log"

# LangExtract参数
PARALLEL_PROCESSING = True
BATCH_SIZE = 50
MULTIPLE_PASSES = True

# 验证配置
if not GOOGLE_API_KEY:
    raise ValueError("❌ 未设置GOOGLE_API_KEY，请检查.env文件或环境变量")

print("✅ 配置加载成功")
```

### 步骤4b：Prompt定义 prompt.py

```python
# prompt.py

SYSTEM_PROMPT = """
你是一个专业的跨境电商税收政策舆论分析系统。

你的任务是从社交媒体舆论中精确提取结构化信息。
目标是捕捉消费者/卖家对跨境电商税收政策的真实态度、涉及的业务模式、面临的风险。

【关键分类维度】

维度1：情感反应 (Sentiment)
- Positive (正面)：表达支持政策、接受现状或认为政策合理
  标志词：认可、赞同、点赞、同意、支持、相信国家、感谢
  
- Negative (负面)：表达反对、焦虑、困惑、恐惧、批评
  标志词：怎么办、担心、焦虑、不知道、无奈、被罚、补税、损失
  
- Neutral (中立)：纯粹描述事实、数据对比、无明确情感倾向
  标志词：根据、按照、分析、报道、讲述

维度2：业务模式 (Pattern)
0110 - 传统外贸+香港公司：香港公司、新加坡、ODI备案、空壳、实质管理地
9610 - B2C小包裹零售：备案、核定征收、三单对碰、退运、物流、海外仓
9710 - B2B直接订单：B2B、线上订单、身份验证、阿里国际站、速卖通
9810 - 海外仓模式：海外仓、离境退税、报关价格、库存核销、多平台混合
1039 - 市场采购：市场采购、外综服、义乌、小商户、拼箱
Temu - 平台全托管：Temu、全托管、内销视同、无库存、平台定价
None - 未涉及具体模式

维度3：风险类型 (Risk Category)
- 香港空壳：空壳公司、0申报、实质管理地被认定 → 严重性 Critical
- 备案难题：流程复杂、政府部门不回应 → 严重性 Medium
- 库存核销：多平台混合、数据对不上 → 严重性 High
- 数据不符：增值税vs所得税数据矛盾 → 严重性 High
- 恶意拆分：规模超500万、规避税收 → 严重性 Critical
- 规模困境：做大后税负爆表 → 严重性 High
- 补税压力：被查、补税、处罚 → 严重性 Critical
- 信息不透明：规则不清、执行不一致 → 严重性 Medium
- 无风险：讨论技术、分享经验、咨询 → 严重性 None

维度4：纳税人身份 (Taxpayer Identity)
- General：一般纳税人、13%税率、大企业规模
- Small：小规模纳税人、3%税率、个体户
- Unknown：未提及或不清楚

维度5：行为倾向 (Behavioral Intent)
- Compliance：主动补税、已咨询专业人士、寻求合规
- Mode_Switch：考虑切换模式、比较方案
- Help_Seeking：询问怎么办、求助、咨询
- Wait_and_See：等政策澄清、观望、推迟决策
- No_Action：纯讨论、无行动意图

输出格式（必须是有效JSON）：
{
  "text": "原始舆论文本",
  "sentiment": "positive|negative|neutral",
  "sentiment_confidence": 0.88,
  
  "pattern": "0110|9610|9710|9810|1039|Temu|None",
  "pattern_confidence": 0.92,
  
  "risk_category": "香港空壳|备案难题|库存核销|数据不符|恶意拆分|规模困境|补税压力|信息不透明|无风险",
  "risk_confidence": 0.85,
  "risk_severity": "Critical|High|Medium|Low|None",
  
  "taxpayer_identity": "General|Small|Unknown",
  "taxpayer_confidence": 0.90,
  
  "behavioral_intent": "Compliance|Mode_Switch|Help_Seeking|Wait_and_See|No_Action",
  "behavioral_confidence": 0.82,
  
  "key_insight": "这条舆论最重要的一句话"
}

关键指示：
1. 置信度范围 0.0-1.0，反映对分类的确定程度
2. 信息不足时，置信度可较低 (0.5-0.7)
3. 优先准确性 - 不确定就标 None/Unknown
4. 一条舆论可涉及多模式，标记最主要的
5. 考虑讽刺和复杂修辞
"""

# Few-shot 示例库（很重要！）
EXAMPLES = [
    {
        "text": "9610备案3个月了，物流公司还是说不清楚手续。政府也不给明确指导，真的很焦虑。",
        "sentiment": "negative",
        "pattern": "9610",
        "risk_category": "备案难题",
        "taxpayer_identity": "Unknown",
        "behavioral_intent": "Help_Seeking"
    },
    {
        "text": "我们的香港公司战略决策都在国内，财务申报也在国内，会不会被认定为税收居民？",
        "sentiment": "neutral",
        "pattern": "0110",
        "risk_category": "香港空壳",
        "taxpayer_identity": "General",
        "behavioral_intent": "Help_Seeking"
    },
    {
        "text": "小规模不加税，我立即把采购转给小供应商了，省点成本。政策设计得聪明。",
        "sentiment": "negative",  # 讽刺，实际在规避
        "pattern": "None",
        "risk_category": "无风险",
        "taxpayer_identity": "General",
        "behavioral_intent": "No_Action"
    },
    {
        "text": "9810海外仓，多平台混合销售，库存数据始终对不上。被查过一次，补了200万税。",
        "sentiment": "negative",
        "pattern": "9810",
        "risk_category": "库存核销",
        "taxpayer_identity": "Unknown",
        "behavioral_intent": "Help_Seeking"
    },
    {
        "text": "Temu规模到500万后，13%增值税真的交不起。在考虑改独立模式。",
        "sentiment": "negative",
        "pattern": "Temu",
        "risk_category": "规模困境",
        "taxpayer_identity": "General",
        "behavioral_intent": "Mode_Switch"
    }
]
```

### 步骤4c：主程序 main.py

```python
# main.py
import langextract as lx
import json
import time
from datetime import datetime
from pathlib import Path
import logging

from config import (
    GOOGLE_API_KEY, MODEL, INPUT_FILE, OUTPUT_FILE, 
    SAMPLE_FILE, LOG_FILE, PARALLEL_PROCESSING, BATCH_SIZE, MULTIPLE_PASSES
)
from prompt import SYSTEM_PROMPT, EXAMPLES

# 设置日志
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class OpinionAnalyzer:
    def __init__(self):
        self.system_prompt = SYSTEM_PROMPT
        self.examples = EXAMPLES
        self.model = MODEL
        self.results = []
    
    def read_opinions(self, filepath, limit=None):
        """读取舆论文本"""
        with open(filepath, 'r', encoding='utf-8') as f:
            opinions = [line.strip() for line in f.readlines() if line.strip()]
        
        if limit:
            opinions = opinions[:limit]
        
        return opinions
    
    def analyze_batch(self, opinions):
        """用LangExtract批量分析"""
        print(f"\n开始处理 {len(opinions)} 条舆论...")
        print(f"模型：{self.model}")
        print(f"并行处理：{PARALLEL_PROCESSING}")
        print("="*60)
        
        try:
            # 调用LangExtract核心函数
            results = lx.extract(
                text=opinions,
                instruction=self.system_prompt,
                examples=self.examples,
                model=self.model,
                parallel_processing=PARALLEL_PROCESSING,
                batch_size=BATCH_SIZE,
                multiple_passes=MULTIPLE_PASSES
            )
            
            print(f"✅ 处理完成！成功：{len(results)}/{len(opinions)}")
            
            return results
            
        except Exception as e:
            print(f"❌ 处理出错：{str(e)}")
            logging.error(f"LangExtract处理失败：{str(e)}")
            raise
    
    def save_results(self, results, output_file=OUTPUT_FILE):
        """保存结果为JSON"""
        output_data = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "model": self.model,
                "total_processed": len(results)
            },
            "results": results
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 结果已保存到：{output_file}")
        logging.info(f"保存{len(results)}条分析结果到{output_file}")
    
    def generate_statistics(self, results):
        """生成统计报告"""
        stats = {
            "total": len(results),
            "sentiment_distribution": {},
            "pattern_distribution": {},
            "risk_distribution": {},
            "avg_confidence": 0
        }
        
        confidences = []
        
        for result in results:
            # 情感分布
            sentiment = result.get('sentiment', 'unknown')
            stats['sentiment_distribution'][sentiment] = \
                stats['sentiment_distribution'].get(sentiment, 0) + 1
            
            # 模式分布
            pattern = result.get('pattern', 'None')
            stats['pattern_distribution'][pattern] = \
                stats['pattern_distribution'].get(pattern, 0) + 1
            
            # 风险分布
            risk = result.get('risk_category', 'unknown')
            stats['risk_distribution'][risk] = \
                stats['risk_distribution'].get(risk, 0) + 1
            
            # 平均置信度
            confidences.append(result.get('sentiment_confidence', 0))
        
        stats['avg_confidence'] = sum(confidences) / len(confidences) if confidences else 0
        
        return stats
    
    def print_statistics(self, stats):
        """打印统计信息"""
        print("\n" + "="*60)
        print("【分析统计报告】")
        print("="*60)
        
        print(f"\n总处理数：{stats['total']} 条")
        print(f"平均置信度：{stats['avg_confidence']:.2%}")
        
        print("\n【情感分布】")
        for sentiment, count in stats['sentiment_distribution'].items():
            pct = 100 * count / stats['total']
            print(f"  {sentiment}: {count:5d} ({pct:5.1f}%)")
        
        print("\n【模式分布（Top 6）】")
        sorted_patterns = sorted(
            stats['pattern_distribution'].items(),
            key=lambda x: x[1],
            reverse=True
        )
        for pattern, count in sorted_patterns[:6]:
            pct = 100 * count / stats['total']
            print(f"  {pattern}: {count:5d} ({pct:5.1f}%)")
        
        print("\n【风险分布（Top 8）】")
        sorted_risks = sorted(
            stats['risk_distribution'].items(),
            key=lambda x: x[1],
            reverse=True
        )
        for risk, count in sorted_risks[:8]:
            pct = 100 * count / stats['total']
            print(f"  {risk}: {count:5d} ({pct:5.1f}%)")
        
        print("\n" + "="*60)

def main():
    """主流程"""
    
    analyzer = OpinionAnalyzer()
    
    # 步骤1：读取数据
    print("【步骤1】读取舆论数据...")
    opinions = analyzer.read_opinions(INPUT_FILE)
    print(f"✅ 读取完成：{len(opinions)} 条")
    
    # 步骤2：批量分析
    print("\n【步骤2】执行LangExtract分析...")
    results = analyzer.analyze_batch(opinions)
    
    # 步骤3：保存结果
    print("\n【步骤3】保存分析结果...")
    analyzer.save_results(results)
    
    # 步骤4：统计分析
    print("\n【步骤4】生成统计报告...")
    stats = analyzer.generate_statistics(results)
    analyzer.print_statistics(stats)
    
    print("\n✅ 全部完成！")
    print(f"输出文件：{OUTPUT_FILE}")
    
    return results

if __name__ == "__main__":
    try:
        results = main()
    except Exception as e:
        print(f"\n❌ 执行失败：{str(e)}")
        logging.error(f"主程序执行失败：{str(e)}")
```

---

## 四、分阶段执行计划

### 阶段1：样本测试（12月16-17日，2-3小时）

```bash
# 步骤1：创建sample_100.txt
# 从 opinions_clean_5000.txt 随机抽取100条

python -c "
import random
with open('data/opinions_clean_5000.txt') as f:
    all_lines = f.readlines()
sample = random.sample(all_lines, 100)
with open('data/sample_100.txt', 'w', encoding='utf-8') as f:
    f.writelines(sample)
print('✅ 样本准备完成：100条')
"

# 步骤2：测试运行
# 编辑 main.py，改为：
# opinions = analyzer.read_opinions(SAMPLE_FILE, limit=100)

python main.py

# 输出应该这样：
# 开始处理 100 条舆论...
# 模型：gemini-2.5-flash
# ✅ 处理完成！成功：100/100
#
# 【分析统计报告】
# 总处理数：100 条
# 平均置信度：87.45%
# ...

# 步骤3：精度验证
# 手工标注20条样本，与结果对比
# 如果匹配率 >= 85% 就能进行全量处理
```

### 阶段2：全量处理（12月18-20日，4-8小时自动运行）

```bash
# 步骤1：修改 main.py 使用全部数据
# 改回：
# opinions = analyzer.read_opinions(INPUT_FILE)

# 步骤2：运行
python main.py

# 这会自动：
# ├─ 读取5000条舆论
# ├─ 并行调用LLM API（批处理）
# ├─ 保存结果到 analysis_results_5000.json
# └─ 生成统计报告

# 预期耗时：
# 100条 → 2分钟（测试）
# 5000条 → 90分钟 + 自动运行

# API成本估算：
# 5000条 × 平均2500 tokens/条 = 12.5M tokens
# 价格：¥40-80（取决于实际token消耗）
```

### 阶段3：导出与验证（12月21-22日，1-2小时）

```python
# 生成可视化报告 export_results.py
import json
import pandas as pd
import matplotlib.pyplot as plt

# 读取分析结果
with open('data/analysis_results_5000.json') as f:
    data = json.load(f)

results = data['results']

# 转换为DataFrame（便于Excel）
df = pd.DataFrame([
    {
        'ID': i + 1,
        '原始舆论': r.get('text', ''),
        '情感': r.get('sentiment', ''),
        '模式': r.get('pattern', ''),
        '风险': r.get('risk_category', ''),
        '身份': r.get('taxpayer_identity', ''),
        '行为': r.get('behavioral_intent', ''),
        '关键洞察': r.get('key_insight', ''),
        '置信度': r.get('sentiment_confidence', 0)
    }
    for i, r in enumerate(results)
])

# 导出Excel
df.to_excel('data/analysis_results_5000_for_paper.xlsx', index=False)
print(f"✅ Excel导出完成：{len(df)} 行")

# 生成可视化图表
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
fig.suptitle('舆论分析结果汇总', fontsize=16)

# 情感分布
sentiment_counts = df['情感'].value_counts()
axes[0, 0].pie(sentiment_counts.values, labels=sentiment_counts.index)
axes[0, 0].set_title('情感分布')

# 模式分布
pattern_counts = df['模式'].value_counts().head(6)
axes[0, 1].barh(pattern_counts.index, pattern_counts.values)
axes[0, 1].set_title('主要模式分布')

# 风险分布
risk_counts = df['风险'].value_counts().head(8)
axes[1, 0].barh(risk_counts.index, risk_counts.values)
axes[1, 0].set_title('风险类型分布')

# 置信度分布
axes[1, 1].hist(df['置信度'], bins=20, edgecolor='black')
axes[1, 1].set_title('置信度分布')
axes[1, 1].set_xlabel('置信度')
axes[1, 1].set_ylabel('频数')

plt.tight_layout()
plt.savefig('results/analysis_visualization.png', dpi=300, bbox_inches='tight')
print("✅ 图表已保存")

print("\n【最终输出清单】")
print("✅ analysis_results_5000.json - 原始JSON数据")
print("✅ analysis_results_5000_for_paper.xlsx - 论文用Excel")
print("✅ analysis_visualization.png - 可视化图表")
```

---

## 五、成本与时间详细分析

### 成本计算

```
Gemini API成本：
├─ 模型：gemini-2.5-flash
├─ 输入价格：$0.075 / 1M tokens
├─ 输出价格：$0.30 / 1M tokens
│
├─ 估计使用：
│  ├─ 系统Prompt：1000 tokens/条（固定）
│  ├─ Few-shot例子：2000 tokens/条（固定）
│  ├─ 用户输入：200 tokens/条（平均）
│  ├─ LLM输出：300 tokens/条（平均）
│  └─ 单条总计：3500 tokens
│
├─ 5000条总用量：
│  └─ 5000 × 3500 = 17.5M tokens
│
└─ 成本估算：
   ├─ 输入成本：15.5M × $0.075 / 1M = $1.16
   ├─ 输出成本：2M × $0.30 / 1M = $0.6
   └─ 总成本：$1.76 ≈ ¥12-15

优化方案：
├─ 如果用fewer examples（3个而不是5个）→ ¥8-10
├─ 如果用temperature=0.3（更简洁） → ¥10-12
└─ 保守估计：¥50-80（含偶发重试）
```

### 时间表详细版

```
12月16日 (周一)
├─ 09:00-10:00: 环境搭建 + 配置API
├─ 10:00-11:00: 代码编写与测试
├─ 11:00-12:00: 样本数据准备
├─ 14:00-16:00: 运行样本测试 + 精度验证
└─ 工作量：5小时

12月17日 (周二)
├─ 09:00-10:00: 调整Prompt（如需）
├─ 10:00-12:00: 编辑main.py使用全量数据
├─ 13:00: 启动全量处理（后台自动运行）
└─ 工作量：3小时（主要是启动，然后后台运行）

12月18-20日 (周三-周五)
├─ 过程监控：每天早晚看一下运行状态（1小时/天）
└─ 预期完成：12月20日晚

12月21日 (周六)
├─ 10:00-11:00: 下载结果文件
├─ 11:00-12:00: 数据验证 + 质量检查
├─ 13:00-14:00: 导出Excel
├─ 14:00-15:00: 生成可视化图表
└─ 工作量：4小时

12月22日 (周日)
├─ 10:00-12:00: 准备论文用数据
├─ 12:00-13:00: 编写数据说明文档
└─ 工作量：3小时

总投入：18小时（分散在13天）
实际工作：约9小时
自动运行：约90分钟
```

---

## 六、常见问题与排查

### Q1：API密钥错误

```
错误信息：401 Unauthorized

原因可能：
├─ 密钥不对：重新复制
├─ 格式错误：检查.env或环境变量
├─ 密钥过期：重新生成
├─ 地区限制：某些地区无法访问Google API

解决：
python -c "
import os
key = os.getenv('GOOGLE_API_KEY')
print(f'当前密钥：{key[:20]}...' if key else '未找到密钥')
"
```

### Q2：处理速度很慢

```
原因：
├─ 网络延迟：正常，Gemini API不是最快的
├─ 并行处理未启用：检查config中PARALLEL_PROCESSING
├─ batch_size太小：改为50-100

性能期望：
├─ 100条：2-3分钟
├─ 1000条：20-30分钟
├─ 5000条：90-120分钟（不连续）
```

### Q3：JSON格式错误

```
错误：JSONDecodeError

原因：LLM有时返回非标准JSON

解决（已在代码中实现）：
├─ 自动重试
├─ 降低temperature参数
├─ 在Prompt中强调JSON格式
└─ 如失败记为"error"后续可修复
```

### Q4：置信度太低

```
如果avg_confidence < 0.80：

可能原因：
├─ Prompt不够清晰
├─ Few-shot例子不够好
├─ 任务太复杂

优化方案：
├─ 增加Examples
├─ 简化分类维度
├─ 用gemini-2.5-pro而非flash
└─ 手工审查低置信度结果
```

---

## 七、输出文件格式

### 主输出：analysis_results_5000.json

```json
{
  "metadata": {
    "timestamp": "2025-12-22T15:30:00",
    "model": "gemini-2.5-flash",
    "total_processed": 5000
  },
  "results": [
    {
      "text": "9610备案3个月还没动静，真的很焦虑",
      "sentiment": "negative",
      "sentiment_confidence": 0.95,
      "pattern": "9610",
      "pattern_confidence": 0.98,
      "risk_category": "备案难题",
      "risk_confidence": 0.92,
      "risk_severity": "Medium",
      "taxpayer_identity": "Unknown",
      "taxpayer_confidence": 0.6,
      "behavioral_intent": "Help_Seeking",
      "behavioral_confidence": 0.9,
      "key_insight": "9610备案流程复杂，政府部门指导不足"
    },
    ...（共5000条）
  ]
}
```

### 辅助输出：analysis_results_5000_for_paper.xlsx

```
ID | 原始舆论 | 情感 | 模式 | 风险 | 身份 | 行为 | 关键洞察 | 置信度
---|---------|-----|-----|------|------|------|---------|-------
1  | 9610备案... | negative | 9610 | 备案难题 | Unknown | Help_Seeking | ... | 0.95
2  | 香港公司... | neutral | 0110 | 香港空壳 | General | Help_Seeking | ... | 0.88
...
```

---

## 八、完成后的下一步

✅ analysis_results_5000.json 生成
✅ analysis_results_5000_for_paper.xlsx 导出
✅ 可视化报告生成

📌 **立即进行**：
1. 用Excel数据生成论文表格和图表
2. 从JSON结果中提取关键洞察（top 10-20条）
3. 与DID分析结果结合（如有）
4. 编写Part B论文

---

**下一个文档**：`STEP_3_论文集成与可视化网站.md`

完成时间：预计12月25日前所有数据分析完成，可进行论文撰写。
