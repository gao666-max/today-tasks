@echo off
cd /d "%~dp0"
start http://127.0.0.1:8901
python -m uvicorn main:app --host 127.0.0.1 --port 8901
pause
