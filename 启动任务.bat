@echo off
cd /d "%~dp0"
for /f "tokens=5" %%p in ('netstat -ano ^| findstr :8901 ^| findstr LISTENING') do taskkill /PID %%p /F 2>nul
start http://127.0.0.1:8901
python -m uvicorn main:app --host 127.0.0.1 --port 8901
pause
