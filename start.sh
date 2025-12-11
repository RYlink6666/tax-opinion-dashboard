#!/bin/bash

# 跨境电商舆论爬虫 - Linux/Mac 一键启动脚本

set -e

echo ""
echo "============================================================"
echo "【跨境电商税收舆论爬虫】- 一键启动"
echo "============================================================"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到 Python，请先安装 Python 3.8+"
    exit 1
fi
echo "✅ Python 环境正常"
python3 --version

# 检查 MediaCrawler
echo ""
echo "检查 MediaCrawler..."
if ! python3 -c "from media_crawler.weibo import WeiboCrawler" 2>/dev/null; then
    echo "⚠️  MediaCrawler 未安装，正在安装..."
    git clone https://github.com/NanmiCoder/MediaCrawler.git
    cd MediaCrawler
    pip3 install -e .
    cd ..
fi
echo "✅ MediaCrawler 环境正常"

# 验证配置
echo ""
echo "【验证配置】"
python3 config.py
if [ $? -ne 0 ]; then
    echo "❌ 配置验证失败"
    exit 1
fi

# 启动爬虫
echo ""
echo "============================================================"
echo "【开始采集数据】"
echo "============================================================"
echo ""

echo "🟢 启动微博爬虫（后台运行，24-30小时）"
python3 1_crawl_weibo_mediacrawler.py > /dev/null 2>&1 &
WEIBO_PID=$!
echo "   PID: $WEIBO_PID"

echo "⏳ 等待 5 秒..."
sleep 5

echo ""
echo "🟢 启动知乎爬虫（后台运行，15-20小时）"
python3 2_crawl_zhihu_mediacrawler.py > /dev/null 2>&1 &
ZHIHU_PID=$!
echo "   PID: $ZHIHU_PID"

echo ""
echo "============================================================"
echo "✅ 爬虫已启动！"
echo "============================================================"
echo ""
echo "📌 爬虫将在后台运行，预计耗时："
echo "   - 微博：24-30 小时"
echo "   - 知乎：15-20 小时"
echo ""
echo "📊 监控进度："
echo "   tail -f logs/crawl_weibo.log"
echo "   tail -f logs/crawl_zhihu.log"
echo ""
echo "🔄 数据清洁（爬虫完成后，12月13日）："
echo "   python3 4_merge_and_clean.py"
echo ""
echo "📁 最终输出："
echo "   data/clean/opinions_clean_5000.txt"
echo ""
echo "⏹️  停止爬虫："
echo "   kill $WEIBO_PID"
echo "   kill $ZHIHU_PID"
echo ""
echo "============================================================"
echo ""
