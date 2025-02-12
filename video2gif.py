import subprocess
import sys
import os

def get_video_duration(input_path):
    """获取视频时长"""
    cmd = [
        'ffprobe',
        '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        input_path
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except Exception as e:
        print(f"错误：无法获取视频时长 - {str(e)}")
        sys.exit(1)

def convert_to_gif(input_path):
    """转换视频为高质量GIF"""
    base_dir = os.path.dirname(input_path)
    video_name = os.path.splitext(os.path.basename(input_path))[0]
    output_dir = os.path.join(base_dir, video_name)  # 修改为文件名路径
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, f"{video_name}.gif")

    # 交互参数设置
    duration = get_video_duration(input_path)
    print(f"\n视频时长：{duration:.2f}秒")
    
    start_time = input("输入开始时间（格式HH:MM:SS，默认00:00:00）：") or "00:00:00"
    end_time = input("输入结束时间（格式HH:MM:SS，默认视频结尾）：") or ""
    
    # 高级GIF转换参数
    cmd = [
        'ffmpeg',
        '-y',
        '-ss', start_time,
    ]
    
    if end_time:
        cmd += ['-to', end_time]
    
    cmd += [
        '-i', input_path,
        '-vf', 'fps=15,scale=480:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse=dither=bayer',
        '-loop', '0',
        output_path
    ]

    try:
        subprocess.run(cmd, check=True, stderr=subprocess.DEVNULL)
        print(f"\nGIF生成成功！输出文件：{output_path}")
        print("建议：")
        print("- 文件大小：约1-5MB")
        print("- 分辨率：480px宽")
        print("- 帧率：15fps")
    except subprocess.CalledProcessError:
        print("转换失败，请检查：")
        print("1. FFmpeg是否安装")
        print("2. 时间参数是否有效")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        input("请将视频文件拖放到此窗口，按回车键退出...")
        sys.exit(1)
    
    video_path = sys.argv[1]
    if not os.path.isfile(video_path):
        input("错误：输入文件不存在，按回车键退出...")
        sys.exit(1)
    
    print("\n正在生成GIF...")
    convert_to_gif(video_path)
    input("\n操作完成，按回车键退出...")