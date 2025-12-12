# 运行系统架构图生成脚本
# PowerShell脚本 - 适合Windows

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║          系统架构图生成工具                                 ║" -ForegroundColor Cyan
Write-Host "║    Generating System Architecture Diagram...              ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

Write-Host "`n📊 开始生成图片..." -ForegroundColor Yellow
Write-Host "   脚本位置: $scriptPath" -ForegroundColor Gray
Write-Host "   Python版本检查中..." -ForegroundColor Gray

# 检查Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "   ✅ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Python未安装" -ForegroundColor Red
    exit 1
}

Write-Host "`n正在执行 quick_draw.py..." -ForegroundColor Yellow
python quick_draw.py

if ($?) {
    Write-Host "`n✅ 脚本执行成功！" -ForegroundColor Green
    Write-Host "`n📁 生成的文件：" -ForegroundColor Cyan
    Get-Item -Path "$scriptPath\*.png" -ErrorAction SilentlyContinue | ForEach-Object {
        Write-Host "   ✓ $($_.Name)" -ForegroundColor Green
    }
    Get-Item -Path "$scriptPath\*.pdf" -ErrorAction SilentlyContinue | ForEach-Object {
        Write-Host "   ✓ $($_.Name)" -ForegroundColor Green
    }
} else {
    Write-Host "`n❌ 脚本执行失败" -ForegroundColor Red
}

Write-Host "`n按任意键关闭..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
