# PowerShell脚本 - 后台运行 pretrain_bertopic.py
# 使用方式: .\run_pretrain_background.ps1

$workdir = "f:\研究生经济学\税收经济学科研\最优税收理论\电商舆论数据产品"
$logfile = "$workdir\pretrain_bertopic.log"

Write-Host "Starting BERTopic pretraining in background..."
Write-Host "Log file: $logfile"
Write-Host ""

# 设置环境变量并启动脚本
$env:HF_ENDPOINT = "https://hf-mirror.com"

# 运行脚本，输出到日志
Start-Process -FilePath "python" `
    -ArgumentList "pretrain_bertopic.py" `
    -WorkingDirectory $workdir `
    -RedirectStandardOutput $logfile `
    -RedirectStandardError "$workdir\pretrain_bertopic_error.log" `
    -NoNewWindow

Write-Host "Process started in background."
Write-Host "To check progress: tail -f $logfile (in terminal)"
Write-Host ""
Write-Host "When complete, model will be saved to:"
Write-Host "  streamlit_app/data/bertopic_model/"
