@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: 初始化变量
set "selected_script="
set "file_args="

:: 检查是否通过文件拖放启动
if not "%~1"=="" (
    set "file_args="
    for %%a in (%*) do set "file_args=!file_args! "%%~a""
    call :auto_select_script
    exit /b
)

:main_menu
cls
echo **************** Python脚本执行器 ****************
echo 功能说明：
echo   1. 直接拖放文件到本脚本：自动选择第一个Python脚本处理
echo   2. 双击运行本脚本：选择Python脚本后拖放文件处理
echo   3. 支持处理多个文件/文件夹
echo *************************************************

:: 获取当前目录所有Python脚本
set /a script_count=0
for %%i in (*.py) do (
    set /a script_count+=1
    set "pyfile!script_count!=%%i"
)

:: 无脚本时退出
if %script_count% equ 0 (
    echo 错误：当前目录未找到任何Python脚本！
    pause
    exit /b
)

:: 显示交互菜单
echo.
echo 可用的Python脚本：
echo [0] 退出
for /l %%n in (1,1,%script_count%) do (
    call echo [%%n] %%pyfile%%n%%
)

:: 输入选择
:input_loop
echo.
set "choice="
set /p "choice=请输入要执行的脚本序号 (0-%script_count%)："

:: 强化输入处理 --------------------------------------------------------
:: 步骤1：去除所有空格和引号
set "choice=!choice: =!"
set "choice=!choice:"=!"

:: 步骤2：验证非空输入
if "!choice!"=="" (
    echo 错误：输入不能为空！
    goto input_loop
)

:: 步骤3：验证纯数字格式
echo !choice!|findstr /r "^[0-9][0-9]*$" >nul
if errorlevel 1 (
    echo 错误：'!choice!' 不是有效数字！
    goto input_loop
)

:: 步骤4：转换为数值
set /a num=!choice! 2>nul
if errorlevel 1 (
    echo 错误：'!choice!' 转换为数字失败！
    goto input_loop
)

:: 步骤5：验证数值范围
if !num! lss 0 (
    echo 错误：输入不能小于0！
    goto input_loop
)
if !num! gtr %script_count% (
    echo 错误：输入不能超过%script_count%！
    goto input_loop
)
:: 输入验证结束 --------------------------------------------------------

if !num! equ 0 exit /b

:: 动态获取脚本路径（关键修正）
for /f "tokens=1*" %%a in ("!num!") do (
    set "selected_script=!pyfile%%a!"
)

:: 验证脚本路径
if not defined selected_script (
    echo 错误：找不到对应的Python脚本！
    pause
    goto main_menu
)

:: 获取待处理文件
:get_files
cls
echo 已选择脚本：!selected_script!
echo.
echo 请将需要处理的文件/文件夹拖放到本窗口（支持多个）
echo （完成后直接按回车开始执行）
echo.
set "file_args="
set /p "file_args=拖放文件到此："

:: 执行Python脚本（带路径验证）
if exist "!selected_script!" (
    if defined file_args (
        echo 正在执行：python "!selected_script!" !file_args!
        python "!selected_script!" !file_args!
    ) else (
        echo 未提供输入文件，尝试直接运行脚本...
        python "!selected_script!"
    )
) else (
    echo 错误：Python脚本不存在 - "!selected_script!"
)

:: 完成处理
echo.
echo 执行完成！按任意键返回主菜单...
pause >nul
goto main_menu

:auto_select_script
:: 自动选择第一个脚本（带验证）
if %script_count% geq 1 (
    set "selected_script=!pyfile1!"
    if exist "!selected_script!" (
        echo 检测到拖放文件，自动执行：!selected_script!
        echo 文件列表：%file_args%
        python "!selected_script!" %file_args: = %  # 移除多余空格 
        pause
        exit /b
    )
)
echo 错误：未找到可用Python脚本！
pause
exit /b

:: 若需要更严格的路径处理，可在执行Python命令处稍作调整：
:: python "!selected_script!" !file_args!
:: 将%file_args%改为!file_args!以使用延迟扩展，避免特殊字符被解释。但原修改方案已能处理大多数情况，可根据实际需求选择是否添加此调整。