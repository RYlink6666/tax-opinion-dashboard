@echo off
REM MediaCrawler 爬虫启动脚本 - 使用 uv 运行

chcp 65001 >nul
cd /d "f:\研究生经济学\税收经济学科研\最优税收理论\电商舆论数据产品\MediaCrawler"

echo ============================================================
echo 【启动 MediaCrawler 爬虫】
echo ============================================================
echo.
echo 🟢 启动微博爬虫...
start /min cmd /c "uv run python main.py --platform weibo --keywords 0110,9610,9810,1039,Temu --search_type default --sort_by default --pages 50 --save_data_option csv"

timeout /t 5

echo 🟢 启动知乎爬虫...
start /min cmd /c "uv run python main.py --platform zhihu --keywords 9610,9810,增值税 --sort_by default --pages 30 --save_data_option csv"

echo.
echo ============================================================
echo ✅ 爬虫已启动
echo ============================================================
echo 📁 数据位置：MediaCrawler/data/
echo.
pause
