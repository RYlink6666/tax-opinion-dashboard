# MediaCrawler 快速部署指南

## 第一步：安装 MediaCrawler（5分钟）

```bash
# 1. 克隆仓库
git clone https://github.com/NanmiCoder/MediaCrawler.git
cd MediaCrawler

# 2. 安装依赖
pip install -e .

# 3. 验证安装
python -c "from media_crawler.weibo import WeiboCrawler; print('✅ Weibo爬虫可用')"
python -c "from media_crawler.zhihu import ZhihuCrawler; print('✅ Zhihu爬虫可用')"
python -c "from media_crawler.xhs import XhsCrawler; print('✅ 小红书爬虫可用')"
```

## 第二步：配置项目结构

```
你的项目/
├── MediaCrawler/                 ← 刚克隆的仓库
├── 1_crawl_weibo.py             ← 本文档提供
├── 2_crawl_zhihu.py             ← 本文档提供
├── 3_crawl_xiaohongshu.py       ← 本文档提供
├── 4_data_cleaning.py           ← 本文档提供
├── keywords.json                 ← 关键词配置
├── config.py                     ← 通用配置
└── data/
    ├── raw/
    │   ├── weibo/
    │   ├── zhihu/
    │   └── xiaohongshu/
    └── clean/
        └── opinions_clean_5000.txt
```

## 第三步：配置关键词库

创建 `keywords.json`：

```json
{
  "models": [
    "0110", "香港公司", "新加坡公司", "空壳公司",
    "9610", "9610备案", "核定征收", "三单对碰",
    "9710", "B2B", "线上订单", "身份验证",
    "9810", "海外仓", "库存核销", "报关",
    "1039", "市场采购", "外综服", "义乌",
    "Temu", "全托管", "内销视同"
  ],
  "policies": [
    "增值税", "税收", "政策", "补税", "合规",
    "税负", "涨价", "跨境电商", "报税"
  ],
  "sentiment": [
    "困难", "焦虑", "无奈", "担心", "痛苦",
    "解决", "建议", "咨询", "讨论", "分享"
  ],
  "date_range": {
    "start": "2025-06-01",
    "end": "2025-12-31"
  },
  "target_volume": {
    "weibo": 2500,
    "zhihu": 1500,
    "xiaohongshu": 800,
    "total": 4800
  }
}
```

## 第四步：查看对应的爬虫脚本

- `1_crawl_weibo.py` - 微博爬虫
- `2_crawl_zhihu.py` - 知乎爬虫
- `3_crawl_xiaohongshu.py` - 小红书爬虫
- `4_data_cleaning.py` - 数据清洁脚本

## 运行顺序

```bash
# 1. 微博采集（最快，2-3小时）
python 1_crawl_weibo.py

# 2. 知乎采集（中等，3-4小时）
python 2_crawl_zhihu.py

# 3. 小红书采集（可选，2-3小时）
python 3_crawl_xiaohongshu.py

# 4. 数据清洁与合并
python 4_data_cleaning.py

# 输出：data/clean/opinions_clean_5000.txt
```

## 常见问题

**Q1：403错误（反爬虫）**
- A: MediaCrawler已处理，会自动轮换User-Agent和延迟

**Q2：某个平台采集速度很慢**
- A: 正常，为避免被封做了延迟。不要改，让它跑

**Q3：采集不到数据**
- A: 检查网络、检查关键词、检查时间范围

**Q4：数据重复度高**
- A: 数据清洁脚本会去重，见第4步

---

准备好了吗？看下一个文件：`1_crawl_weibo.py`
