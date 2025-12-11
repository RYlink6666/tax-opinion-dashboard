@echo off
REM 分析缺失的900条记录
REM 需要先设置 ZHIPU_API_KEY 环境变量或直接在脚本中配置

cd /d "%~dp0"

echo.
echo ====================================================
echo  跨境电商税收舆论分析 - 缺失记录分析
echo ====================================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

REM 检查依赖
echo ⏳ 检查依赖...
pip show zhipuai >nul 2>&1
if errorlevel 1 (
    echo ❌ 未安装zhipuai，正在安装...
    pip install zhipuai
)

echo.
echo 🚀 启动分析...
echo.

REM 运行分析脚本
python analyze_missing_900.py

if errorlevel 1 (
    echo.
    echo ❌ 分析失败
    pause
    exit /b 1
) else (
    echo.
    echo ✅ 分析完成！
    pause
)
