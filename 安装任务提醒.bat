@echo off
set "PYW=pythonw.exe"
for /f "delims=" %%i in ('where pythonw.exe 2^>nul') do set "PYW=%%i"
schtasks /Create /F /TN "ZhengXinTasksReminder" /TR "%PYW% %~dp0remind.py" /SC DAILY /ST 09:00
pause
