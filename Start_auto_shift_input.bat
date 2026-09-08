@echo off
cd /d "%~dp0"
start "Auto Shift Input" "%~dp0env\Scripts\pythonw.exe" "%~dp0auto_shift_input.py"
