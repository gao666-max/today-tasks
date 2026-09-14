@echo off
schtasks /Create /F /TN "ZhengXinTasksReminder" /TR "D:\mini\pythonw.exe %~dp0remind.py" /SC DAILY /ST 09:00
pause
