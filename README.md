# bakatools

一些自己日常用的小脚本，简单无脑使用，运行环境为 Windows 系统，其他系统未测试~  
不是程序员，不会敲代码，纯兴趣爱好和为了自己方便，大部分代码是通过 AI 辅助生成，自己再根据看得懂的部分和注释修改而成。  
需要 python 的运行环境，windows 可以直接微软商店安装，会默认配置好环境。

# 批处理

批处理运行模板，选择自己喜欢的方式使用即可。

## baka.bat

多脚本批处理模板，放在相应的脚本文件夹，选择要用的脚本即可。

<details>

### 功能说明

- 自动扫描当前目录所有.py 文件，动态生成带编号的脚本列表
- 单个脚本时自动确认执行，多个脚本时显示选择菜单
- 支持拖放文件，中英文路径和文件名，会自动识别需不需要引号

### 小技巧

要优先执行特定脚本，可在文件名前加数字排序，例如：

```
00_videosplitter.py
01_videocut.py
```

需要管理员权限时，在 bat 文件开头添加：

```
fltmc >nul 2>&1 || (
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    echo UAC.ShellExecute "%~s0", "", "", "runas", 1 >> "%temp%\getadmin.vbs"
    "%temp%\getadmin.vbs"
    del "%temp%\getadmin.vbs"
    exit /b
)
```

需要指定 Python 版本时，修改执行命令为：

```
"C:\Python310\python.exe" "%%a" %*
```

</details>

## baaka.bat

单脚本批处理模板，修改运行脚本名称运行对应脚本。

# 脚本

各种小工具的简单使用说明，会慢慢根据需求补充。

## Video

依赖于 ffmpeg，需要安装对应环境依赖：

```
pip install ffmpeg-python
```

具体配置可以看脚本内注释修改。

<details>

### video_splitter

视频无损分割，输入视频分割时间节点，即可切割（1 个节点分割成 2 份，2 个分割成 3 份，以此类推），输入完成后按两下 `Enter` 即可确认。

配合 mpv 的复制当前时间快捷键可以更方便的使用。

### video_cut

视频无损切片，输入开始时间和结束时间，输入完成后按两下 `Enter` 即可确认。

配合 mpv 的复制当前时间快捷键可以更方便的使用。

### video_delete

视频片段无损删除，输入片段前后时间点，切除不想要的视频片段，并将剩余的片段合并。因关键帧对齐，最终视频可能会比原视频稍短。

配合 mpv 的复制当前时间快捷键可以更方便的使用。

### video_merger

对相同录制参数的视频，按照从先到后的顺序合并为一个新的视频。

### video_2mp4

无损转换视频为 mp4 格式，支持批量文件和文件夹混合输入。

### video_2social

转换视频为普通清晰度的 mp4 格式，并转换为 30 帧，适合直接将视频分享到 qq 群、X 等社交媒体平台的情况。

### video_2gif

转换视频为普通清晰度的 gif 动图，适合直接将短视频做成动图分享到 qq 群等社交媒体平台的情况。

建议配合 video2social 使用。

### video_compress

通用的压制视频的脚本，不常用。

### ytb_coverdl

批量下载 youtube 视频封面，在保存位置用 txt 格式建立文本文件，填入图片网址，每行一个，不需要符号分割。

</details>

## Anime

### anime_sort

对动漫资源进行文件分类整理，适配 emby 的命名规则。

<details>

以 VCB-Studio 的资源为例：

```
- anime_sort
    - CM        # 电视放送广告
    - IV        # 节目、采访、舞台活动、制作
    - Menus     # BD/DVD 播放选择菜单
    - OPED      # 无字 OP/ED
    - PV        # 预告片
```

将`SPs`文件夹直接拖入`SPs通用整理.bat`，会自动根据文件夹内文件文件名关键词创建相关文件夹和元数据，分类放入对应的文件夹内，直接将分类文件夹移动至季文件夹同一目录下，例如：

```
- 碧蓝之海 (2018)
    - Season 1 (2018) [UHA-WINGS@VCB-Studio] # 第一季文件
    - PV        # 预告片
```

最终在 emby 资源库季末尾显示，效果如下：

![emby预览](anime/anime_sort/preview.webp)

如需要识别大小写，则在批处理程序中修改运行脚本文件为`sp_sort_Aa.py`。

如是 VCB-Studio 的资源，可直接将下载整个文件夹拖入`VCB-Studio整理专用.bat`，脚本会显示对应动漫的 TMDB 链接，填入第几季、季年份、动漫中文名称后，在通用分类的基础上，还会对文件进行重命名以适配 emby：

```
- 碧蓝之海 (2018)
    - [VCB-Studio] Grand Blue [Ma10p_1080p]
        - [VCB-Studio] Grand Blue [01][Ma10p_1080p][x265_flac_aac].mkv
-------------  ↓  -----------------
- 碧蓝之海 (2018)
    - Season 1 (2018) [VCB-Studio]
        - 碧蓝之海 - S01E01 - 1080p.mkv
```

</details>
