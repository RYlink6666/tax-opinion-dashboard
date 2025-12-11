# Start Streamlit App
cd "$PSScriptRoot\streamlit_app"
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host "Starting Streamlit Dashboard..." -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host ""
Write-Host "Open your browser and navigate to: http://localhost:8501" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

streamlit run main.py --client.email=
