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

def get_time_points():
    """获取用户输入的时间点"""
    print("请输入分割时间点（格式：HH:MM:SS，直接回车结束输入）")
    time_points = []
    
    while True:
        try:
            user_input = input(f"时间点 {len(time_points)+1}: ").strip()
            if not user_input:
                break
                
            valid, seconds = validate_time(user_input)
            if not valid:
                print(f"错误：'{user_input}' 不是有效时间（必须为 HH:MM:SS 且数值合法）")
                continue
                
            time_points.append((user_input, seconds))
        except KeyboardInterrupt:
            print("\n操作已取消")
            sys.exit(1)
            
    return [tp[0] for tp in sorted(time_points, key=lambda x: x[1])]

def split_video(input_path, time_points):
    """使用 ffmpeg 分割视频"""
    output_dir = os.path.join(os.path.dirname(input_path), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    filename = os.path.splitext(os.path.basename(input_path))[0]
    extension = os.path.splitext(input_path)[1]
    
    # 获取视频总时长
    total_duration = get_video_duration(input_path)
    hours, remainder = divmod(total_duration, 3600)
    minutes, seconds = divmod(remainder, 60)
    end_time = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
    
    # 添加最后一个片段到视频结尾
    time_points.append("end")
    
    start_time = "00:00:00"
    for idx, end_time in enumerate(time_points, 1):
        output_path = os.path.join(
            output_dir,
            f"{filename}_part{idx}{extension}"
        )
        
        cmd = [
            "ffmpeg",
            "-y",  # 覆盖输出文件
            "-ss", start_time,
            "-i", input_path
        ]
        
        # 非最后一段需要添加-to参数
        if end_time != "end":
            cmd += ["-to", end_time]
        
        cmd += [
            "-c:v", "copy",
            "-c:a", "copy",
            output_path
        ]
        
        try:
            subprocess.run(cmd, check=True, stderr=subprocess.DEVNULL)
            print(f"成功生成片段 {idx}: {start_time} → {end_time if end_time != 'end' else '视频结尾'}")
            start_time = end_time
        except subprocess.CalledProcessError:
            print(f"错误：无法生成片段 {idx}，请检查 ffmpeg 是否安装")
            sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        input("请将视频文件拖放到此窗口，按回车键退出...")
        sys.exit(1)
    
    video_path = sys.argv[1]
    if not os.path.isfile(video_path):
        input("错误：输入文件不存在，按回车键退出...")
        sys.exit(1)
    
    time_points = get_time_points()
    if not time_points:
        input("错误：未输入任何时间点，按回车键退出...")
        sys.exit(1)
    
    print("\n即将按以下时间点分割视频：")
    print(" → ".join(["00:00:00"] + time_points + ["视频结尾"]))
    if input("确认分割？(y/n): ").lower() != 'y':
        print("操作已取消")
        sys.exit(0)
    
    split_video(video_path, time_points)
    print("\n视频分割完成！输出目录：", os.path.join(os.path.dirname(video_path), "output"))
    input("按回车键退出...")