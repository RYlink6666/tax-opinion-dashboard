@echo off
chcp 65001 >nul
cd /d %~dp0

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║     跨境电商舆论分析 - 数据清洁 (PHASE 1)                    ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

echo [1/3] 检查环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到Python，请先安装Python
    pause
    exit /b 1
)
echo ✓ Python环境正常

echo.
echo [2/3] 检查依赖...
pip list | findstr "pandas" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  正在安装pandas...
    pip install pandas openpyxl -q
    echo ✓ pandas已安装
) else (
    echo ✓ pandas已安装
)

echo.
echo [3/3] 开始清洁数据...
echo 数据来源: MediaCrawler/data/xhs/json/
echo 输出位置: data/clean/
echo.
python 4_merge_and_clean.py

if errorlevel 1 (
    echo.
    echo ❌ 清洁失败！
    pause
    exit /b 1
)

echo.
echo ✅ 清洁完成！
echo.
echo 📊 下一步：
echo    python 5_llm_analyze.py （需要12.16日开始）
echo.
pause
