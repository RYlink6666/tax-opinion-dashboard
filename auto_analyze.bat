@echo off
REM 自动分析脚本启动器（Windows）
REM 功能：运行auto_analyze.py进行数据分析和推送

setlocal enabledelayedexpansion

REM 获取脚本所在目录
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM 日志文件
set LOG_FILE=%SCRIPT_DIR%auto_analyze.log
set TIMESTAMP=%date:~0,4%-%date:~5,2%-%date:~8,2% %time:~0,2%:%time:~3,2%:%time:~6,2%

echo.
echo ============================================================
echo 🚀 跨境电商税收舆论分析 - 自动更新
echo ============================================================
echo 时间: %TIMESTAMP%
echo 脚本位置: %SCRIPT_DIR%
echo.

REM 写入日志
(
    echo.
    echo ============================================================
    echo 运行时间: %TIMESTAMP%
    echo ============================================================
) >> "%LOG_FILE%"

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：未找到Python
    echo 请确保已安装Python 3.8+
    echo 可以在此下载: https://www.python.org/downloads/
    goto END
)

echo ✓ Python已安装
python --version
echo.

REM 检查依赖
echo 📦 检查依赖...
python -m pip install -q requests pandas zhipuai streamlit

REM 检查Zhipu API Key
if "%ZHIPU_API_KEY%"=="" (
    echo.
    echo ⚠️  警告：未设置ZHIPU_API_KEY环境变量
    echo 设置方法：
    echo.
    echo 方法1（临时，仅本次有效）：
    echo   set ZHIPU_API_KEY=your_api_key_here
    echo   python auto_analyze.py
    echo.
    echo 方法2（永久，推荐）：
    echo   1. 控制面板 → 系统和安全 → 系统 → 高级系统设置
    echo   2. 环境变量 → 新建 → 变量名: ZHIPU_API_KEY
    echo   3. 变量值: 你的API密钥
    echo.
    set /p ZHIPU_API_KEY="请输入ZHIPU_API_KEY (或按Enter跳过): "
)

echo.
echo 🔄 运行分析脚本...
echo.

REM 运行分析脚本并记录日志
python auto_analyze.py >> "%LOG_FILE%" 2>&1
set ERROR_CODE=!errorlevel!

echo.
if !ERROR_CODE! equ 0 (
    echo ✅ 分析完成！
    echo 📊 查看日志: %LOG_FILE%
    echo 🌐 访问网站: https://tax-opinion-dashboard-atbvxazynv7jcjpsjhdvzh.streamlit.app/
) else (
    echo ❌ 分析失败！错误代码: !ERROR_CODE!
    echo 📊 查看日志: %LOG_FILE%
)

:END
echo.
echo ============================================================
pause
