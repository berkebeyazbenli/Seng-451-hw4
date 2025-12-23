@echo off
REM Windows için başlatma scripti

echo Starting Backend and Frontend...

REM Backend'i arka planda başlat
start "Backend" cmd /k "uvicorn main:app --reload --port 8000"

REM 3 saniye bekle
timeout /t 3 /nobreak >nul

REM Frontend'i başlat
echo Starting Frontend...
streamlit run app.py

