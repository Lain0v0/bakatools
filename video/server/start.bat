@echo off
chcp 65001 >nul
title VRChat 本地视频服务器 - 多语言支持

echo ========================================
echo    VRChat 本地视频服务器启动程序
echo ========================================
echo   多语言支持: 简体中文, 繁體中文, English, 日本語, 한국어
echo ========================================
echo.

:: 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未检测到Python，请先安装Python 3.x
    echo 可以从 https://www.python.org/downloads/ 下载
    pause
    exit /b 1
)

:: 检查依赖库
echo 检查必要的依赖库...
pip list | findstr "Flask" >nul
if errorlevel 1 (
    echo 安装Flask库...
    pip install flask
)

pip list | findstr "flask-cors" >nul
if errorlevel 1 (
    echo 安装flask-cors库...
    pip install flask-cors
)

echo.
echo 依赖库检查完成！
echo.

:: 创建video目录（如果不存在）
if not exist "video" (
    echo 创建video目录...
    mkdir video
    echo 请将视频文件放入新创建的video文件夹中
    echo.
)

:: 显示video目录中的文件和对应的URL
echo 检测到的视频文件及对应URL:
echo ========================================
setlocal enabledelayedexpansion
set "count=0"
set "url_list="

if exist "video" (
    for /f "delims=" %%i in ('dir video /b 2^>nul') do (
        set /a count+=1
        set "filename=%%i"
        set "url=http://localhost:14514/video/%%i"
        echo !count!. !filename!
        echo    !url!
        echo.
        set "url_list=!url_list!!count!. !url!¬"
    )
)

if !count! equ 0 (
    echo 未找到视频文件
    echo 请将MP4、AVI、MOV等视频文件放入video文件夹
)

echo ========================================
echo.
echo 视频URL列表（可直接复制）:
echo ========================================
setlocal disabledelayedexpansion
if defined url_list (
    set "temp=!url_list!"
    :loop
    for /f "tokens=1* delims=¬" %%a in ("!temp!") do (
        if not "%%a"=="" (
            echo %%a
            set "temp=%%b"
        )
    )
    if defined temp goto :loop
) else (
    echo 暂无视频文件
)
echo ========================================
echo.

echo 启动视频服务器...
echo 按 Ctrl+C 停止服务器
echo 服务器启动后，可在浏览器右上角切换语言
echo 支持语言: 简体中文, 繁體中文, English, 日本語, 한국어
echo 注意: 只可以在非公开世界使用
echo.

:: 运行Python服务器
python video_server.py

pause
