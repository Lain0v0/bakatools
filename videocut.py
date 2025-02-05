import re
import subprocess
import sys
import os

def get_video_duration(input_path):
    """使用ffprobe获取视频总时长（秒）"""
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
    except (subprocess.CalledProcessError, ValueError) as e:
        print(f"错误：无法获取视频时长 - {str(e)}")
        sys.exit(1)

def validate_time(time_str):
    """验证时间格式 HH:MM:SS 并转换为秒数"""
    if not re.match(r'^\d{2}:\d{2}:\d{2}$', time_str):
        return False, None
    
    try:
        hours, minutes, seconds = map(int, time_str.split(':'))
        if not (0 <= hours < 24 and 0 <= minutes < 60 and 0 <= seconds < 60):
            return False, None
        total_seconds = hours * 3600 + minutes * 60 + seconds
        return True, total_seconds
    except ValueError:
        return False, None

def get_time_range(total_duration):
    """获取时间范围"""
    # 转换总时长为可读格式
    hours, remainder = divmod(total_duration, 3600)
    minutes, seconds = divmod(remainder, 60)
    max_time = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
    
    print(f"\n视频总时长：{max_time}")
    
    while True:
        try:
            # 获取开始时间
            start = input("请输入开始时间 (HH:MM:SS): ").strip()
            valid_start, start_sec = validate_time(start)
            if not valid_start:
                print(f"错误：'{start}' 不是有效时间")
                continue

            # 获取结束时间
            end = input("请输入结束时间 (HH:MM:SS): ").strip()
            valid_end, end_sec = validate_time(end)
            if not valid_end:
                print(f"错误：'{end}' 不是有效时间")
                continue

            # 验证时间顺序
            if start_sec >= end_sec:
                print("错误：开始时间必须早于结束时间")
                continue

            # 验证不超过视频总时长
            if end_sec > total_duration:
                print(f"警告：结束时间超过视频总时长，已自动调整为 {max_time}")
                return start, max_time

            return start, end

        except KeyboardInterrupt:
            print("\n操作已取消")
            sys.exit(1)

def cut_video(input_path, start_time, end_time):
    """使用 ffmpeg 剪切视频"""
    output_dir = os.path.join(os.path.dirname(input_path), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    filename = os.path.splitext(os.path.basename(input_path))[0]
    extension = os.path.splitext(input_path)[1]
    
    output_path = os.path.join(
        output_dir,
        f"{filename}_clip{extension}"
    )
    
    cmd = [
        "ffmpeg",
        "-y",          # 覆盖输出文件
        "-ss", start_time,
        "-to", end_time,
        "-i", input_path,
        "-c:v", "copy", # 视频流复制
        "-c:a", "copy", # 音频流复制
        output_path
    ]
    
    try:
        subprocess.run(cmd, check=True, stderr=subprocess.DEVNULL)
        print(f"\n成功生成片段：{start_time} → {end_time}")
        print("输出文件：", output_path)
    except subprocess.CalledProcessError:
        print("错误：无法生成片段，请检查：")
        print("1. FFmpeg 是否安装")
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
    
    # 获取视频信息
    total_duration = get_video_duration(video_path)
    
    # 获取时间范围
    start, end = get_time_range(total_duration)
    
    # 确认操作
    print(f"\n即将截取时间段：{start} → {end}")
    if input("确认剪切？(y/n): ").lower() != 'y':
        print("操作已取消")
        sys.exit(0)
    
    # 执行剪切
    cut_video(video_path, start, end)
    input("\n操作完成，按回车键退出...")