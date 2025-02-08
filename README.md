# bakatools

一些自己日常用的小脚本，简单无脑使用，运行环境为Windows系统，其他系统未测试~  
不是程序员，不会敲代码，纯兴趣爱好和为了自己方便，大部分代码是通过AI辅助生成，自己再根据看得懂的部分和注释修改而成。  
需要python的运行环境，windows可以直接微软商店安装，会默认配置好环境。

## runpy.bat

直接运行批处理程序，选择要用的脚本即可。

### 功能说明

- 自动扫描当前目录所有.py文件，动态生成带编号的脚本列表
- 单个脚本时自动确认执行，多个脚本时显示选择菜单
- 支持拖放文件，中英文路径和文件名

注意非当前文件夹路径需要英文的双引号，例如 `"C:\Users\"` ）

### 小技巧

要优先执行特定脚本，可在文件名前加数字排序，例如：
```
00_videosplitter.py
01_videocut.py
```

需要管理员权限时，在bat文件开头添加：
```
fltmc >nul 2>&1 || (
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    echo UAC.ShellExecute "%~s0", "", "", "runas", 1 >> "%temp%\getadmin.vbs"
    "%temp%\getadmin.vbs"
    del "%temp%\getadmin.vbs"
    exit /b
)
```

需要指定Python版本时，修改执行命令为：
```
"C:\Python310\python.exe" "%%a" %*
```

# list

各种小工具的简单使用说明，会慢慢根据需求补充。

## video

依赖于ffmpeg，需要安装对应环境依赖：
```
pip install ffmpeg-python
```

### videosplitter

视频无损分割，输入视频分割时间节点，即可切割（1个节点分割成2份，2个分割成3份，以此类推），输入完成后按两下  `Enter` 即可确认。

配合mpv的复制当前时间快捷键可以更方便的使用。

### videocut

视频无损切片，输入开始时间和结束时间，输入完成后按两下  `Enter` 即可确认。

配合mpv的复制当前时间快捷键可以更方便的使用。

### videodelete

视频片段无损删除，输入片段前后时间点，切除不想要的视频片段，并将剩余的片段合并。因关键帧对齐，最终视频可能会比原视频稍短。

配合mpv的复制当前时间快捷键可以更方便的使用。

### video2mp4

转换视频为普通清晰度的mp4格式，适合直接将视频分享到qq群等社交媒体平台的情况。

### video2gif

转换视频为普通清晰度的gif动图，适合直接将短视频做成动图分享到qq群等社交媒体平台的情况。

建议配合video2mp4使用。

