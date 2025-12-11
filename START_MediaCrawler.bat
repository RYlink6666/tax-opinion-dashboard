@echo off
REM 跨境电商舆论爬虫 - MediaCrawler 版本（已安装依赖）

chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ============================================================
echo 【跨境电商税收舆论爬虫】- MediaCrawler 版本启动
echo ============================================================
echo.

REM 切换到 MediaCrawler 目录
cd /d MediaCrawler

REM 使用 uv 运行爬虫
echo 🟢 启动微博爬虫（后台运行）
start /min .venv\Scripts\python.exe -m media_crawler.weibo --keywords "0110,9610,9810,1039,Temu,增值税,跨境电商" --pages 50

echo ⏳ 等待 5 秒...
timeout /t 5 /nobreak

echo.
echo 🟢 启动知乎爬虫（后台运行）
start /min .venv\Scripts\python.exe -m media_crawler.zhihu --keywords "9610,9810,增值税,跨境电商" --pages 30

echo.
echo ============================================================
echo ✅ MediaCrawler 爬虫已启动！
echo ============================================================
echo.
echo 📌 爬虫将在后台运行
echo.
echo 📊 数据位置：MediaCrawler/data/
echo.
echo ============================================================
echo.
pause
