@echo off
cd /d "%~dp0"
cd streamlit_app
echo Starting Streamlit application...
echo Open browser at http://localhost:8501
echo.
timeout /t 3 /nobreak
start http://localhost:8501
streamlit run main.py --client.email=
pause
