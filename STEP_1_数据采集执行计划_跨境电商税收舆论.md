# 第一阶段：数据采集执行计划
## 跨境电商税收舆论分析项目（2025年12月）

**项目目标**：采集5000条跨境电商税收政策相关舆论数据  
**周期**：12月10-20日（完成采集）  
**成本**：¥0-200（众包备选）  
**产出**：opinions_clean_5000.txt（标准格式）

---

## 一、数据采集方案汇总

### 1.1 你现有的资源

```
已有框架：
├─ 弹性论文项目的爬虫框架（针对商品价格）
├─ 众包渠道（阿里众包/腾讯众包）
├─ 爬虫经验（有多个SPIDER脚本）
└─ 数据存储体系（数据库 + 文件系统）
```

### 1.2 采集策略（三层递进）

```
第1层：API自动采集（0成本）
├─ 微博API（开发者账号免费额度）
├─ 知乎API（有限制但免费）
└─ 小红书API（需研究可行性）

第2层：网页爬虫（¥0，时间成本）
├─ 微博网页版爬虫（Selenium）
├─ 知乎网页版爬虫（BeautifulSoup）
├─ 小红书网页版爬虫（Puppeteer或Selenium）
└─ 电商论坛（55BBS等跨境论坛）

第3层：众包补充（¥100-200，备选）
├─ 招聘众包采集人员采集评论
├─ 指导词汇：避孕品、增值税、政策等
└─ 品控：质量审核后导入
```

---

## 二、立即开始的实操（今天-明天）

### 步骤1：确认采集关键词（1小时）

基于你的电商舆论数据产品，关键词应该是：

```
跨境电商相关：
├─ 0110: 香港公司、新加坡、ODI备案、空壳
├─ 9610: 9610模式、备案、核定征收、三单对碰
├─ 9710: B2B、线上订单、身份验证、阿里国际站
├─ 9810: 海外仓、库存、报关、退税
├─ 1039: 市场采购、外综服、义乌、拼箱
├─ Temu: 全托管、内销、平台定价
└─ 通用词: 跨境电商、税收、政策、补税、涨价

政策时间点：
├─ 2025-11中旬：税收政策宣布期
├─ 2025-12：政策讨论期
├─ 2026-01-01：政策实施期
└─ 2026-02+：后续反应期

采集时间范围：
└─ 2025-06-01 至 2025-12-31（6个月）
```

**保存为 `keywords.json`**：

```json
{
  "platforms": ["weibo", "zhihu", "xiaohongshu", "tiktok"],
  "keywords": {
    "models": ["0110", "9610", "9710", "9810", "1039", "Temu", "跨境电商"],
    "policies": ["增值税", "税收", "政策", "补税"],
    "sentiment": ["涨价", "税负", "合规", "便宜"]
  },
  "date_range": {
    "start": "2025-06-01",
    "end": "2025-12-31"
  },
  "target_volume": 5000
}
```

---

### 步骤2：调查现有数据（1-2小时）

检查你的电商舆论数据产品项目中是否已有数据：

```bash
# 检查以下目录
f:/研究生经济学/税收经济学科研/最优税收理论/电商舆论数据产品/

# 可能存在的数据文件
├─ scraped_data/        # 爬虫产出
├─ raw_data/            # 原始数据
├─ weibo_posts/         # 微博数据
├─ zhihu_answers/       # 知乎数据
└─ *.csv / *.json       # 导出文件

检查清单：
□ 是否已有微博/知乎数据？
□ 数据量多少条？
□ 时间范围覆盖6个月吗？
□ 数据质量如何（重复率、有效性）？
```

**快速数据统计脚本**：

```python
import os
import json
import pandas as pd

# 扫描现有数据
for file in os.listdir('scraped_data/'):
    if file.endswith('.csv'):
        df = pd.read_csv(f'scraped_data/{file}')
        print(f"{file}: {len(df)} 条数据")
    elif file.endswith('.json'):
        with open(f'scraped_data/{file}') as f:
            data = json.load(f)
            print(f"{file}: {len(data)} 条数据")

# 统计总体
print(f"\n当前数据状态：")
print(f"总条数：{total_count}")
print(f"平台分布：{platform_dist}")
print(f"时间覆盖：{date_range}")
print(f"数据缺口：{gap}")
```

---

### 步骤3：快速爬虫采集（当前周末）

如果数据不足，用现有爬虫框架快速补充。

#### 方案A：用你的RealSpider框架（推荐）

```bash
# 位置：
f:/研究生经济学/税收经济学科研/最优税收理论/国际税收单开/弹性论文/real_spider_framework/

# 这个框架已经有：
├─ JD_REAL_SPIDER.py         # 京东爬虫（可改为微博）
├─ MANMANBUY_SCRAPER.py      # 漫买网爬虫（可改为知乎）
└─ integrated_real_spider.py  # 综合爬虫框架

# 修改建议：
# 1. 创建 WEIBO_SPIDER.py（基于RealSpider框架改造）
# 2. 创建 ZHIHU_SPIDER.py
# 3. 创建 XIAOHONGSHU_SPIDER.py
```

**快速Weibo爬虫（基于你的框架）**：

```python
# weibo_spider_quick.py
import requests
import json
import time
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import random

class WeiboSpider:
    def __init__(self, keywords, start_date='2025-06-01', end_date='2025-12-31'):
        self.keywords = keywords
        self.start_date = start_date
        self.end_date = end_date
        self.posts = []
        
    def search_weibo(self, keyword, pages=10):
        """搜索微博（使用网页版，无需API）"""
        
        for page in range(1, pages + 1):
            # 微博搜索URL
            url = f"https://s.weibo.com/weibo?q={keyword}&typeall=1&suball=1&timescope=custom%3A2025-06-01-0-2025-12-31-23&page={page}"
            
            headers = {
                'User-Agent': self._random_user_agent(),
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
            }
            
            try:
                response = requests.get(url, headers=headers, timeout=10)
                response.encoding = 'utf-8'
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # 提取帖子
                posts = soup.find_all('div', class_='mbrank')
                for post in posts:
                    try:
                        text = post.find('p', class_='txt').text.strip()
                        like = post.find('span', class_='like-count')
                        like_count = int(like.text) if like else 0
                        
                        self.posts.append({
                            'platform': 'weibo',
                            'keyword': keyword,
                            'text': text,
                            'likes': like_count,
                            'source_url': url
                        })
                    except:
                        continue
                
                # 防止被封IP
                time.sleep(random.uniform(2, 5))
                
            except Exception as e:
                print(f"错误: {e}")
                continue
    
    def _random_user_agent(self):
        agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        ]
        return random.choice(agents)
    
    def save_results(self, filename='weibo_posts_raw.json'):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.posts, f, ensure_ascii=False, indent=2)
        print(f"✅ 保存 {len(self.posts)} 条数据到 {filename}")

# 使用示例
spider = WeiboSpider(
    keywords=['0110', '9610', '9710', '9810', '1039', 'Temu', '跨境电商', '增值税'],
    start_date='2025-06-01',
    end_date='2025-12-31'
)

for keyword in spider.keywords:
    print(f"正在采集：{keyword}")
    spider.search_weibo(keyword, pages=5)  # 每个关键词采集5页

spider.save_results()
```

**运行方式**：

```bash
# 1. 保存上面的代码为 weibo_spider_quick.py
# 2. 安装依赖
pip install requests beautifulsoup4

# 3. 运行采集
python weibo_spider_quick.py

# 预期：采集1000-2000条微博数据（2-4小时）
```

---

#### 方案B：用知乎API（更稳定）

```python
# zhihu_spider_api.py
import requests
import json
import time

class ZhihuSpider:
    def __init__(self):
        self.base_url = "https://api.zhihu.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def search(self, keyword, pages=10):
        results = []
        
        for page in range(1, pages + 1):
            url = f"{self.base_url}/search?q={keyword}&type=content&page={page}"
            
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                data = response.json()
                
                for item in data.get('data', []):
                    results.append({
                        'platform': 'zhihu',
                        'keyword': keyword,
                        'title': item.get('title', ''),
                        'content': item.get('content', ''),
                        'likes': item.get('voteup_count', 0),
                        'comments': item.get('comment_count', 0),
                        'url': item.get('url', '')
                    })
                
                time.sleep(2)  # 防止被封
                
            except Exception as e:
                print(f"错误: {e}")
        
        return results

# 使用示例
spider = ZhihuSpider()
keywords = ['0110模式', '9610备案', '跨境电商税收', '增值税改革']

all_results = []
for kw in keywords:
    results = spider.search(kw, pages=5)
    all_results.extend(results)
    print(f"{kw}: 采集 {len(results)} 条")

# 保存
with open('zhihu_posts.json', 'w', encoding='utf-8') as f:
    json.dump(all_results, f, ensure_ascii=False, indent=2)

print(f"✅ 总共采集 {len(all_results)} 条知乎数据")
```

---

### 步骤4：数据清洁与格式化（2-3小时）

采集完数据后，统一格式为标准的 `opinions_clean_5000.txt`：

```python
# data_cleaning.py
import json
import pandas as pd
import re

def clean_weibo_data(weibo_json_file):
    """清洁微博数据"""
    with open(weibo_json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    cleaned = []
    for item in data:
        text = item.get('text', '').strip()
        
        # 去除链接、@符号、emoji
        text = re.sub(r'http\S+', '', text)  # 去链接
        text = re.sub(r'@\w+', '', text)     # 去@号
        text = re.sub(r'[^\u4e00-\u9fff\w\s]', '', text)  # 去emoji
        
        # 去除过短的文本
        if len(text) >= 10:
            cleaned.append(text)
    
    # 去重
    cleaned = list(set(cleaned))
    
    return cleaned

def clean_zhihu_data(zhihu_json_file):
    """清洁知乎数据"""
    with open(zhihu_json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    cleaned = []
    for item in data:
        # 知乎：优先用content，其次用title
        text = item.get('content', '') or item.get('title', '')
        text = text.strip()
        
        # 同样的清洁流程
        text = re.sub(r'http\S+', '', text)
        text = re.sub(r'@\w+', '', text)
        text = re.sub(r'[^\u4e00-\u9fff\w\s]', '', text)
        
        if len(text) >= 10:
            cleaned.append(text)
    
    cleaned = list(set(cleaned))
    return cleaned

def merge_and_save(weibo_clean, zhihu_clean, output_file='opinions_clean_5000.txt'):
    """合并所有数据并保存"""
    all_data = weibo_clean + zhihu_clean
    
    # 再次去重（跨平台）
    all_data = list(set(all_data))
    
    # 统计
    print(f"微博数据：{len(weibo_clean)} 条")
    print(f"知乎数据：{len(zhihu_clean)} 条")
    print(f"合并后：{len(all_data)} 条")
    print(f"去重率：{100 * (1 - len(all_data) / (len(weibo_clean) + len(zhihu_clean))):.1f}%")
    
    # 保存为标准格式（每行一条）
    with open(output_file, 'w', encoding='utf-8') as f:
        for text in all_data:
            f.write(text + '\n')
    
    print(f"\n✅ 清洁完成！保存到 {output_file}")
    print(f"总条数：{len(all_data)}")
    
    # 质量检查：随机抽10条看看
    print("\n【质量抽样（前10条）】")
    for i, text in enumerate(all_data[:10], 1):
        print(f"{i}. {text[:100]}...")
    
    return all_data

# 执行流程
if __name__ == "__main__":
    print("=== 数据清洁开始 ===\n")
    
    # 清洁微博数据
    print("处理微博数据...")
    weibo_clean = clean_weibo_data('weibo_posts_raw.json')
    
    # 清洁知乎数据
    print("处理知乎数据...")
    zhihu_clean = clean_zhihu_data('zhihu_posts.json')
    
    # 合并保存
    print("合并与保存...")
    all_opinions = merge_and_save(weibo_clean, zhihu_clean)
    
    print("\n=== 数据清洁完成 ===")
```

**运行命令**：

```bash
python data_cleaning.py

# 输出示例：
# 微博数据：2400 条
# 知乎数据：1800 条
# 合并后：4050 条
# 去重率：12.5%
# ✅ 清洁完成！保存到 opinions_clean_5000.txt
```

---

## 三、如果采集不足（备选方案）

如果到12月15日还没采集到5000条，使用众包补充：

### 众包采集方案（¥100-200）

```
平台选择：
├─ 阿里众包（https://crowdsourcing.aliyun.com）
├─ 腾讯众包（https://crowdsourcing.tencent.com）
└─ 快手众包（https://www.kwai-baokao.com）

发布任务（每个平台）：
├─ 任务名：《跨境电商税收政策舆论采集》
├─ 数量：500-1000条（分批）
├─ 单价：¥0.2-0.5 / 条
├─ 描述：
│  "采集关于跨境电商增值税政策的真实评论。
│   包括：0110/9610/9810/1039模式相关讨论，
│   政策宣布期（2025-11中旬）到实施期（2026-01）的舆论。
│   来源：微博、知乎、小红书、论坛等社交媒体。
│   不要翻译、不要改写，保留原文。"
│
├─ 质量控制：
│  □ 非重复（与已有数据不重复）
│  □ 中文文本（不要英文）
│  □ 长度20-500字符
│  □ 真实来源（标注平台）

预期时间：3-5天完成
总成本：¥100-200
```

**采集数据验收表**：

```python
def validate_crowdsourcing_data(csv_file):
    """验收众包数据质量"""
    df = pd.read_csv(csv_file)
    
    issues = []
    
    for idx, row in df.iterrows():
        text = row['text']
        
        # 检查1：长度
        if len(text) < 10 or len(text) > 500:
            issues.append(f"行{idx}: 长度不符（{len(text)}字）")
        
        # 检查2：非中文
        if not any('\u4e00' <= c <= '\u9fff' for c in text):
            issues.append(f"行{idx}: 非中文内容")
        
        # 检查3：重复
        # ...（与既有数据对比）
    
    print(f"✅ 总条数：{len(df)}")
    print(f"❌ 问题条数：{len(issues)}")
    print(f"验收率：{100 * (len(df) - len(issues)) / len(df):.1f}%")
    
    if issues:
        print("\n【问题详情】")
        for issue in issues[:20]:  # 只显示前20个
            print(f"  - {issue}")
```

---

## 四、完整的时间表

```
12月10日（今天）
├─ □ 确认采集关键词（1h）
├─ □ 检查现有数据（1-2h）
└─ □ 部署爬虫脚本（1h）

12月11-13日（周末）
├─ □ 运行Weibo爬虫（4-6h自动运行）
├─ □ 运行Zhihu爬虫（2-3h自动运行）
└─ □ 监控运行状态，处理错误

12月14-15日（周一-周二）
├─ □ 下载采集数据（1h）
├─ □ 数据清洁（2-3h）
├─ □ 数据质量检查（1h）
└─ □ 如果不足5000条，启动众包（可选）

12月16日
├─ □ 众包数据验收（如有）（1h）
├─ □ 最终数据整合（1h）
└─ □ 保存 opinions_clean_5000.txt

12月20日前
└─ □ 准备好用于LLM分析
```

---

## 五、输出标准

最终输出文件格式：

### 文件1：opinions_clean_5000.txt

```
格式：每行一条舆论
编码：UTF-8
行数：≥4800条（允许10%损耗）

示例内容：
---
0110香港公司，战略决策都在深圳，会不会被认定为税收居民？
9610备案已经3个月了还没审批，太难了
小规模纳税人不加税，我就转向小店去买
Temu做到500万规模后，13%增值税真的交不起
1039规模超过500万就不能用了，我们现在很纠结
---

【质量指标】
- 总行数：5000
- 平均长度：100-300字符
- 重复率：<5%
- 有效率：>95%
```

### 文件2：data_summary.json（可选但推荐）

```json
{
  "total_count": 5000,
  "data_source": {
    "weibo": 2400,
    "zhihu": 1800,
    "xiaohongshu": 500,
    "others": 300
  },
  "date_range": {
    "start": "2025-06-01",
    "end": "2025-12-31"
  },
  "keyword_distribution": {
    "0110": 450,
    "9610": 800,
    "9710": 320,
    "9810": 520,
    "1039": 380,
    "Temu": 650,
    "other": 1800
  },
  "quality_metrics": {
    "duplicate_rate": 0.03,
    "valid_rate": 0.97,
    "avg_length": 180,
    "collection_date": "2025-12-15"
  }
}
```

---

## 六、完成后的下一步

一旦 `opinions_clean_5000.txt` 准备好，立即进行**LLM分析**：

```
立即启动（12月16日）：
├─ 复制LangExtract代码（见下文）
├─ 配置API密钥
├─ 测试100条样本
└─ 12月20日前完成全部分析

使用方案（选择一个）：
├─ A) 直接用LangExtract（推荐）- 见下一个文档
├─ B) 用智谱清言API（可选）- 见电商舆论产品文档
└─ C) 混合LangExtract + Amp AI（最优）- 见混合方案报告
```

---

**数据采集阶段完成标志**：
✅ opinions_clean_5000.txt 文件已生成
✅ 文件包含≥4800条有效舆论
✅ 数据覆盖6个月时间范围
✅ 支持用于后续LLM分析

---

**下一个文档**：`STEP_2_LangExtract数据分析计划.md`
