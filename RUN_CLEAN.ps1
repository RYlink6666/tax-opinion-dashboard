# 跨平台数据清洁脚本

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     跨境电商舆论分析 - 数据清洁 (PHASE 1)                    ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/3] 检查环境..." -ForegroundColor Yellow
try {
    python --version | Out-Null
    Write-Host "✓ Python环境正常" -ForegroundColor Green
} catch {
    Write-Host "❌ 未找到Python" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[2/3] 检查依赖..." -ForegroundColor Yellow
$pandas_check = pip list | Select-String "pandas"
if ($null -eq $pandas_check) {
    Write-Host "⚠️  正在安装pandas..." -ForegroundColor Yellow
    pip install pandas openpyxl -q
    Write-Host "✓ pandas已安装" -ForegroundColor Green
} else {
    Write-Host "✓ pandas已安装" -ForegroundColor Green
}

Write-Host ""
Write-Host "[3/3] 开始清洁数据..." -ForegroundColor Yellow
Write-Host "数据来源: MediaCrawler/data/xhs/json/" -ForegroundColor Gray
Write-Host "输出位置: data/clean/" -ForegroundColor Gray
Write-Host ""

python 4_merge_and_clean.py

if ($LastExitCode -ne 0) {
    Write-Host ""
    Write-Host "❌ 清洁失败！" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✅ 清洁完成！" -ForegroundColor Green
Write-Host ""
Write-Host "📊 下一步：" -ForegroundColor Cyan
Write-Host "   python 5_llm_analyze.py （需要12.16日开始）" -ForegroundColor Gray
Write-Host ""
