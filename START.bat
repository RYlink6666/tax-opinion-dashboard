@echo off
REM 跨境电商舆论爬虫 - Windows 一键启动脚本

chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ============================================================
echo 【跨境电商税收舆论爬虫】- 一键启动
echo ============================================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：未找到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)
echo ✅ Python 环境正常

REM 检查 MediaCrawler
python -c "from media_crawler.weibo import WeiboCrawler" >nul 2>&1
if errorlevel 1 (
    echo.
    echo ⚠️  MediaCrawler 未安装，正在安装...
    git clone https://github.com/NanmiCoder/MediaCrawler.git
    cd MediaCrawler
    pip install -e .
    cd ..
)
echo ✅ MediaCrawler 环境正常

REM 验证配置
echo.
echo 【验证配置】
python config.py
if errorlevel 1 (
    echo ❌ 配置验证失败
    pause
    exit /b 1
)

REM 启动爬虫
echo.
echo ============================================================
echo 【开始采集数据】
echo ============================================================
echo.
echo 🟢 启动微博爬虫（后台运行，24-30小时）
start /min cmd /c python 1_crawl_weibo_mediacrawler.py

echo ⏳ 等待 5 秒...
timeout /t 5 /nobreak

echo.
echo 🟢 启动知乎爬虫（后台运行，15-20小时）
start /min cmd /c python 2_crawl_zhihu_mediacrawler.py

echo.
echo ============================================================
echo ✅ 爬虫已启动！
echo ============================================================
echo.
echo 📌 爬虫将在后台运行，预计耗时：
echo    - 微博：24-30 小时
echo    - 知乎：15-20 小时
echo.
echo 📊 监控进度：
echo    查看日志：logs\crawl_weibo.log 或 logs\crawl_zhihu.log
echo.
echo 🔄 数据清洁：
echo    爬虫完成后（12月13日），运行：
echo    python 4_merge_and_clean.py
echo.
echo 📁 最终输出：
echo    data\clean\opinions_clean_5000.txt
echo.
echo ============================================================
echo.
pause
