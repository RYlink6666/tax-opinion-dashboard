@echo off
chcp 65001 > nul
echo.
echo ========================================
echo   GitHub 自动推送脚本
echo ========================================
echo.

cd /d "f:\研究生经济学\税收经济学科研\最优税收理论\电商舆论数据产品"

echo 检查当前状态...
git status --short

echo.
echo 执行推送: git push origin main
echo.

git push origin main

if %errorlevel% equ 0 (
    echo.
    echo ✅ 推送成功！
    echo.
    git log --oneline -1
) else (
    echo.
    echo ❌ 推送失败（错误代码: %errorlevel%）
    echo 请检查：
    echo   1. 网络连接
    echo   2. GitHub凭证（控制面板 ^> 凭证管理器）
    echo   3. 本地提交是否存在
)

echo.
pause
