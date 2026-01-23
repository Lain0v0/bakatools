@echo off
chcp 65001 >nul
cls
echo ========================================
echo   Quick Gallery Generator
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found
    pause
    exit /b 1
)

echo Scanning current directory and starting server...
echo.

python gallery_generator.py . --serve

pause
