@echo off
chcp 65001 >nul

REM Get the directory of the batch file
set SCRIPT_DIR=%~dp0

REM Call the Python script with all the arguments
python "%SCRIPT_DIR%<填脚本文件名>.py" %*

pause
