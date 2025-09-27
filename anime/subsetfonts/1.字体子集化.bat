@echo off
chcp 65001 >nul

REM Get the directory of the batch file
set SCRIPT_DIR=%~dp0

REM 切换到批处理文件所在目录
cd /d "%SCRIPT_DIR%"

REM 运行子集化脚本
.\assfonts.exe -r "%~1" %*
pause

