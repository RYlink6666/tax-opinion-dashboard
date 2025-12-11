# MediaCrawler 爬虫完整运行指南

## 快速开始（5分钟）

### 第0步：环境检查

```bash
# 验证 Python 环境
python --version  # 应该是 3.8+

# 验证 MediaCrawler 已安装
python -c "from media_crawler.weibo import WeiboCrawler; print('✅ OK')"
```

### 第1步：运行爬虫

```bash
# 方式1：分别运行（推荐）
python 1_crawl_weibo_mediacrawler.py      # 微博（2-3小时）
python 2_crawl_zhihu_mediacrawler.py      # 知乎（3-4小时）
python 3_crawl_xiaohongshu_mediacrawler.py # 小红书（可选，2小时）

# 方式2：一键运行所有（创建run_all.sh）
bash run_all_crawlers.sh
```

### 第2步：数据清洁

```bash
# 合并、去重、清洁所有平台数据
python 4_merge_and_clean.py

# 输出：data/clean/opinions_clean_5000.txt
```

### 第3步：验证结果

```bash
# 检查清洁后的数据文件
ls -lh data/clean/opinions_clean_5000.txt

# 查看前几条
head -20 data/clean/opinions_clean_5000.txt

# 统计条数
wc -l data/clean/opinions_clean_5000.txt
```

---

## 详细参数说明

### 配置文件：config.py

这是核心配置，里面定义了：

```python
# 关键词库（自动加载）
FLAT_KEYWORDS = [
    "0110", "9610", "9710", "9810", "1039", "Temu",
    "增值税", "税收", "政策", "补税", ...
]

# 采集目标
TARGET_VOLUMES = {
    "weibo": 2500,         # 微博目标
    "zhihu": 1500,         # 知乎目标
    "xiaohongshu": 800,    # 小红书目标
    "total": 4800          # 总目标
}

# 时间范围
DATE_RANGE = {
    "start": "2025-06-01",
    "end": "2025-12-31"
}

# 清洁参数
CLEAN_CONFIG = {
    "min_length": 10,       # 最小长度
    "max_length": 500,      # 最大长度
    "remove_urls": True,    # 移除URL
    "remove_ads": True      # 过滤广告
}
```

**如需修改参数**：编辑 `config.py` 文件

---

## 常见问题

### Q1：爬虫采集太慢

**A**：这是正常的！为了避免被反爬虫，MediaCrawler 会：
- 轮换 User-Agent
- 使用随机延迟（1-5秒）
- 自动处理限流

**不建议修改延迟参数**，否则容易被封。

预期速度：
- 微博：100条/小时（2500条需要 24-30小时）
- 知乎：100条/小时（1500条需要 15-20小时）
- 小红书：50条/小时（800条需要 16-20小时）

### Q2：某个平台返回 0 条数据

**原因可能**：
1. 关键词不相关
2. 时间范围内没有新的帖子
3. 网络问题（代理被封）
4. API 变更

**解决方案**：
- 检查日志文件 `logs/crawl_*.log`
- 尝试用不同的关键词
- 检查网络连接
- 如持续失败，使用 Mock 数据测试

### Q3：采集到重复数据

**A**：正常现象。去重步骤会处理：
```bash
python 4_merge_and_clean.py
```

会自动：
- 计算内容哈希
- 删除完全重复
- 过滤广告和垃圾

### Q4：能否加快采集速度？

**不推荐**。但如果一定要加快，可以：

1. **使用代理**（需要购买代理服务）
   - 修改 `config.py` 中的 `proxy_enabled: True`
   - 配置代理列表

2. **减少关键词数量**
   - 修改 `config.py` 中的 `FLAT_KEYWORDS`
   - 只保留最重要的 5-10 个关键词

3. **分散采集**
   - 在多台机器上同时运行爬虫

### Q5：数据质量不够好

**检查清单**：

```bash
# 1. 检查数据量
python -c "
import json
with open('data/clean/opinions_clean_5000.json') as f:
    data = json.load(f)
    print(f'总条数：{len(data[\"data\"])}')
"

# 2. 查看样本
head -5 data/clean/opinions_clean_5000.txt

# 3. 查看统计信息
tail -20 logs/clean.log
```

如果数据不足 4800 条，继续运行爬虫直到达标。

### Q6：可以中断吗？

**可以**。爬虫支持中断：
1. 按 `Ctrl+C` 中断
2. 已采集的数据会自动保存
3. 下次运行时会继续采集

---

## 输出文件说明

```
data/
├── raw/
│   ├── weibo/
│   │   └── weibo_raw_20251210_120000.json
│   ├── zhihu/
│   │   └── zhihu_raw_20251210_120000.json
│   └── xiaohongshu/
│       └── xiaohongshu_raw_20251210_120000.json
└── clean/
    ├── opinions_clean_5000.txt        ← 最重要！用于LLM分析
    ├── opinions_clean_5000.json       ← 结构化数据备份
    └── opinions_clean_5000.xlsx       ← Excel表格（可选）

logs/
├── crawl_weibo.log
├── crawl_zhihu.log
├── crawl_xiaohongshu.log
└── clean.log
```

**最重要的输出**：`data/clean/opinions_clean_5000.txt`

这个文件用于下一步的 LLM 分析。

---

## 时间表

```
12月11日启动爬虫
├─ 微博：24-30小时     → 12月12日完成
├─ 知乎：15-20小时     → 12月12日完成
└─ 小红书：16-20小时   → 12月13日完成

12月13日
└─ 运行清洁脚本 → 输出 opinions_clean_5000.txt

12月14日
└─ 开始 LLM 分析（见 STEP_2 文档）
```

---

## 监控运行状态

```bash
# 查看实时日志
tail -f logs/crawl_weibo.log

# 查看采集进度
grep "✓ 获得" logs/crawl_weibo.log

# 统计当前采集数量
python -c "
import json
import glob
total = 0
for f in glob.glob('data/raw/*/weibo_raw_*.json'):
    with open(f) as fp:
        data = json.load(fp)
        total += len(data)
print(f'当前已采集：{total} 条')
"
```

---

## 一键运行脚本（可选）

创建 `run_all_crawlers.sh`：

```bash
#!/bin/bash

echo "【开始运行所有爬虫】"
echo "开始时间：$(date)"

echo "\n[1/3] 开始微博爬虫..."
python 1_crawl_weibo_mediacrawler.py

echo "\n[2/3] 开始知乎爬虫..."
python 2_crawl_zhihu_mediacrawler.py

echo "\n[3/3] 开始数据清洁..."
python 4_merge_and_clean.py

echo "\n【所有任务完成】"
echo "完成时间：$(date)"
echo "\n✅ 输出文件："
ls -lh data/clean/opinions_clean_5000.txt
```

运行：
```bash
chmod +x run_all_crawlers.sh
bash run_all_crawlers.sh
```

---

## 下一步

一旦 `data/clean/opinions_clean_5000.txt` 生成：

1. **LLM 分析**（见 STEP_2 文档）
   ```bash
   python 3_analyze_with_llm.py
   ```

2. **结果导出**
   ```bash
   python 4_export_results.py
   ```

3. **论文集成**
   - 用分析结果生成表格和图表
   - 写 Part B 舆论分析章节

---

## 遇到问题？

检查日志文件：
```bash
cat logs/crawl_weibo.log    # 微博爬虫日志
cat logs/crawl_zhihu.log    # 知乎爬虫日志
cat logs/clean.log          # 清洁日志
```

查看错误信息并对应 "常见问题" 部分。

---

**准备好了吗？** 

运行：`python 1_crawl_weibo_mediacrawler.py`

祝你采集顺利！🚀
