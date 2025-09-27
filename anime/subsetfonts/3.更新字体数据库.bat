@echo off
chcp 65001 >nul

REM Get the directory of the batch file
set SCRIPT_DIR=%~dp0

REM 切换到批处理文件所在目录
cd /d "%SCRIPT_DIR%"

REM 更新字体数据库
.\assfonts.exe -f "D:\Fonts\All" -b
pause
