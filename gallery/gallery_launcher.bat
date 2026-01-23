@echo off
chcp 65001 >nul
cls

echo ========================================
echo   Gallery HTML Generator
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found
    echo Please install Python 3.x from https://www.python.org/downloads/
    timeout /t 3 >nul
    exit /b 1
)

echo Scanning current directory...
echo.

python gallery_generator.py

echo.
echo HTML file generated successfully!
echo Gallery file: gallery.html
timeout /t 2 >nul
