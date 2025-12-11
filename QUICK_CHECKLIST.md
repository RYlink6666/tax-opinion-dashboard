# 🚀 快速启动检查清单

## ✅ 今天必须做的 3 件事

### 1️⃣ 安装 MediaCrawler（15 分钟）

```bash
# 克隆仓库
git clone https://github.com/NanmiCoder/MediaCrawler.git
cd MediaCrawler

# 安装依赖（可能需要pip升级）
pip install -e .

# 验证安装
python -c "from media_crawler.weibo import WeiboCrawler; print('✅')"
```

☐ **验证通过？** 如果看到 ✅，继续下一步

---

### 2️⃣ 配置本项目环境（10 分钟）

```bash
# 回到项目目录
cd 最优税收理论/电商舆论数据产品/

# 验证 config.py 可用
python config.py

# 应该看到：
# ✅ 已加载关键词库：XXX 个关键词
# ✅ 配置验证通过
# ✅ 配置加载成功
```

☐ **配置验证通过？**

---

### 3️⃣ 启动首个爬虫（5 分钟）

```bash
# 微博爬虫（后台自动运行）
python 1_crawl_weibo_mediacrawler.py

# 你会看到：
# 【微博舆论爬虫】- MediaCrawler 版本
# 初始化微博爬虫
# 目标：采集 2500 条数据
# [开始爬取...]
```

☐ **爬虫成功启动？**

---

## 📋 完整检查表

### 环境配置
- [ ] Python 3.8+ 已安装
- [ ] MediaCrawler 已安装（`pip list | grep media-crawler`）
- [ ] 本项目文件结构完整：
  ```
  电商舆论数据产品/
  ├── config.py
  ├── 1_crawl_weibo_mediacrawler.py
  ├── 2_crawl_zhihu_mediacrawler.py
  ├── 3_crawl_xiaohongshu_mediacrawler.py
  ├── 4_merge_and_clean.py
  └── data/
      ├── raw/
      └── clean/
  ```

### 配置文件
- [ ] `config.py` 中的关键词库已加载（20+ 个关键词）
- [ ] 时间范围设置正确（2025-06-01 至 2025-12-31）
- [ ] 采集目标已确认（总计 4800 条）

### 爬虫脚本
- [ ] `1_crawl_weibo_mediacrawler.py` 可运行
- [ ] `2_crawl_zhihu_mediacrawler.py` 可运行
- [ ] `4_merge_and_clean.py` 可运行

### 数据目录
- [ ] `data/raw/weibo/` 目录已创建
- [ ] `data/raw/zhihu/` 目录已创建
- [ ] `data/clean/` 目录已创建
- [ ] `logs/` 目录已创建

---

## 📊 运行顺序

### 第一天（12月11日）
```bash
# 1. 验证环境（10分钟）
python config.py

# 2. 启动微博爬虫（后台运行，24-30小时）
python 1_crawl_weibo_mediacrawler.py &

# 3. 启动知乎爬虫（后台运行，15-20小时）
# 可选：等微博完成后再启动，或在另一台机器上运行
python 2_crawl_zhihu_mediacrawler.py &
```

### 第二天（12月12日）
```bash
# 等待爬虫完成
# 查看进度
tail -f logs/crawl_weibo.log

# 小红书爬虫（可选，2-3小时）
python 3_crawl_xiaohongshu_mediacrawler.py &
```

### 第三天（12月13日）
```bash
# 数据合并与清洁
python 4_merge_and_clean.py

# 验证输出文件
ls -lh data/clean/opinions_clean_5000.txt
wc -l data/clean/opinions_clean_5000.txt  # 应该有 4800+ 行
```

---

## 🔍 实时监控

### 查看爬虫运行状态

```bash
# 微博爬虫日志
tail -f logs/crawl_weibo.log

# 查看采集进度
grep "✓ 获得" logs/crawl_weibo.log | tail -10
```

### 检查采集数据量

```bash
# 动态查看采集数量
python -c "
import json, glob, os
for platform in ['weibo', 'zhihu', 'xiaohongshu']:
    files = glob.glob(f'data/raw/{platform}/*.json')
    total = 0
    for f in files:
        try:
            with open(f) as fp:
                data = json.load(fp)
                total += len(data) if isinstance(data, list) else len(data.get('data', []))
        except:
            pass
    print(f'{platform}: {total} 条')
"
```

---

## ⚠️ 常见问题快速参考

| 问题 | 解决 |
|------|------|
| `ModuleNotFoundError: media_crawler` | 重新安装：`pip install -e MediaCrawler/` |
| 爬虫无输出 | 查看日志：`cat logs/crawl_weibo.log` |
| 采集 0 条数据 | 检查网络、关键词、日志 |
| 采集很慢 | 正常！预期 100 条/小时 |
| 数据重复 | 正常！清洁脚本会去重 |

详见 `RUN_CRAWLERS.md` 的"常见问题"部分。

---

## 📌 关键文件位置

```
你需要关注的文件：

1️⃣ 配置：config.py
   └─ 修改关键词、时间范围、采集目标

2️⃣ 爬虫脚本：
   ├─ 1_crawl_weibo_mediacrawler.py
   ├─ 2_crawl_zhihu_mediacrawler.py
   └─ 4_merge_and_clean.py

3️⃣ 输出文件：data/clean/opinions_clean_5000.txt
   └─ 用于下一步的 LLM 分析

4️⃣ 日志文件：logs/
   ├─ crawl_weibo.log
   ├─ crawl_zhihu.log
   └─ clean.log
```

---

## 🎯 预期结果

### 采集阶段（12月11-13日）
```
微博爬虫：  2500 条 ✓
知乎爬虫：  1500 条 ✓
小红书：     800 条 ✓（可选）
━━━━━━━━━━━━━━━━━━━
总计：      4800+ 条

去重后：    4500+ 条（允许5-10%重复）
清洁后：    4300+ 条（允许10%损耗）
最终：      ≥4000 条（保守估计）
```

### 输出文件
```
✅ data/clean/opinions_clean_5000.txt
   - 每行一条舆论
   - 4000+ 行
   - UTF-8 编码

✅ data/clean/opinions_clean_5000.json
   - 结构化数据
   - 包含元数据（平台、时间等）

✅ logs/clean.log
   - 详细的清洁统计
```

---

## 🚀 准备好了吗？

### 第一步（现在）
```bash
python config.py  # 验证配置
```

### 第二步（5分钟后）
```bash
python 1_crawl_weibo_mediacrawler.py  # 启动爬虫
```

### 第三步（等待 24-30 小时）
```bash
tail -f logs/crawl_weibo.log  # 监控进度
```

### 第四步（12月13日）
```bash
python 4_merge_and_clean.py  # 清洁数据
```

### 第五步（下一个任务）
```bash
# 见 STEP_2_LangExtract完整分析计划.md
python 3_analyze_with_llm.py
```

---

## 📞 需要帮助？

查看对应文件：

- **安装问题**：`0_SETUP_MediaCrawler.md`
- **运行问题**：`RUN_CRAWLERS.md`
- **配置问题**：`config.py`（代码中有注释）
- **数据质量**：`4_merge_and_clean.py`（自动处理）

---

**现在就开始？**

```bash
python config.py && python 1_crawl_weibo_mediacrawler.py
```

Go! 🚀
