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
    """获取用户输入的时间点（新增排序验证）"""
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
    
    # 新增：强制排序并验证时间顺序
    sorted_points = sorted(time_points, key=lambda x: x[1])
    for i in range(1, len(sorted_points)):
        if sorted_points[i][1] <= sorted_points[i-1][1]:
            print(f"错误：时间点必须递增！冲突发生在 {sorted_points[i-1][0]} 和 {sorted_points[i][0]}")
            sys.exit(1)
            
    return [tp[0] for tp in sorted_points]

def split_video(input_path, time_points):
    """使用 ffmpeg 分割视频（关键修复）"""
    base_dir = os.path.dirname(input_path)
    video_name = os.path.splitext(os.path.basename(input_path))[0]
    output_dir = os.path.join(base_dir, video_name)  # 修改为文件名路径
    os.makedirs(output_dir, exist_ok=True)
    
    filename = os.path.splitext(os.path.basename(input_path))[0]
    extension = os.path.splitext(input_path)[1]
    
    # 转换为秒数处理（新增）
    time_seconds = []
    for tp in time_points:
        valid, sec = validate_time(tp)
        time_seconds.append(sec)
    total_duration = get_video_duration(input_path)
    time_seconds.append(total_duration)
    
    # 分割处理逻辑重构
    for idx in range(len(time_seconds)):
        start = time_seconds[idx-1] if idx > 0 else 0
        end = time_seconds[idx]
        
        # 转换为时间字符串（新增）
        def sec_to_time(seconds):
            hours = int(seconds // 3600)
            remainder = seconds % 3600
            minutes = int(remainder // 60)
            seconds = int(remainder % 60)
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        output_path = os.path.join(
            output_dir,
            f"{filename}_part{idx+1}{extension}"
        )
        
        # FFmpeg命令优化（关键修改）
        cmd = [
            "ffmpeg",
            "-y",
            "-ss", str(start),
            "-to", str(end),
            "-i", input_path,
            "-c:v", "copy",
            "-c:a", "copy",
            output_path
        ]
        
        try:
            subprocess.run(cmd, check=True, stderr=subprocess.DEVNULL)
            print(f"成功生成片段 {idx+1}: {sec_to_time(start)} → {sec_to_time(end)}")
        except subprocess.CalledProcessError:
            print(f"错误：无法生成片段 {idx+1}")
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
    print("\n视频分割完成！输出目录：", os.path.join(os.path.dirname(video_path), "视频文件名"))
    input("按回车键退出...")