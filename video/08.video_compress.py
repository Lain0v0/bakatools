import sys
import os
import subprocess
from pathlib import Path

def process_file(input_path):
    # 生成输出路径
    input_path = Path(input_path)
    output_path = input_path.with_stem(f"{input_path.stem}_compressed").with_suffix(".mkv")
    
    # 构建FFmpeg命令
    ffmpeg_cmd = [
        "ffmpeg",
        "-y",  # 覆盖已存在文件
        "-i", str(input_path),
        "-c:v", "av1_nvenc",
        "-preset", "p6",
        "-cq", "20",
        "-g", "120",  # 关键帧间隔60fps*2s=120
        "-bf", "4",  # 最大B帧数
        "-profile:v", "0",
        "-tune", "hq",
        "-multipass", "2",
        "-rc-lookahead", "20",
        "-psy-rd", "1",  # 心理视觉调整
        "-c:a", "copy",  # 音频直接复制
        "-map", "0",  # 包含所有流
        str(output_path)
    ]

    # 执行命令
    try:
        subprocess.run(ffmpeg_cmd, check=True, stderr=subprocess.STDOUT)
        print(f"成功转换: {input_path} -> {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"转换失败: {input_path}\n错误信息: {e.output}")

def process_path(path):
    if os.path.isfile(path):
        process_file(path)
    elif os.path.isdir(path):
        for root, _, files in os.walk(path):
            for file in files:
                if file.lower().endswith(('.mp4', '.mov', '.avi', '.mkv', '.flv')):
                    process_file(os.path.join(root, file))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("请将视频文件或文件夹拖放到脚本上运行")
        sys.exit(1)

    for path in sys.argv[1:]:
        if os.path.exists(path):
            process_path(path)
        else:
            print(f"路径不存在: {path}")

    print("所有转换任务已完成")
    input("按回车键退出...")