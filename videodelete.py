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

def get_cut_segments():
    """获取要删除的时间段"""
    segments = []
    print("请输入要删除的时间段（格式：开始时间 结束时间）")
    print("示例：00:01:30 00:02:15")
    print("输入完成后直接按回车继续")

    while True:
        try:
            user_input = input(f"时间段 {len(segments)+1}: ").strip()
            if not user_input:
                break

            # 验证输入格式
            if len(user_input.split()) != 2:
                print("错误：请输入开始时间和结束时间，用空格分隔")
                continue

            start_str, end_str = user_input.split()
            
            # 验证时间格式
            valid_start, start_sec = validate_time(start_str)
            valid_end, end_sec = validate_time(end_str)
            
            if not (valid_start and valid_end):
                print("错误：时间格式无效，必须为 HH:MM:SS")
                continue

            # 验证时间顺序
            if start_sec >= end_sec:
                print("错误：开始时间必须早于结束时间")
                continue

            segments.append((start_sec, end_sec, start_str, end_str))

        except KeyboardInterrupt:
            print("\n操作已取消")
            sys.exit(1)

    return sorted(segments, key=lambda x: x[0])

def validate_segments(segments, total_duration):
    """验证时间段有效性"""
    last_end = 0
    for i, (start, end, start_str, end_str) in enumerate(segments):
        # 检查时间重叠
        if start < last_end and i > 0:
            print(f"错误：时间段重叠 {start_str} 与上一个时间段结束时间冲突")
            return False
        
        # 检查超出视频时长
        if end > total_duration:
            print(f"错误：结束时间 {end_str} 超过视频总时长")
            return False
        
        last_end = end
    
    return True

def generate_keep_segments(segments, total_duration):
    """生成需要保留的时间段"""
    keep_segments = []
    last_end = 0

    for start, end, _, _ in segments:
        if start > last_end:
            keep_segments.append((last_end, start))
        last_end = end

    # 添加最后一个保留段
    if last_end < total_duration:
        keep_segments.append((last_end, total_duration))

    return keep_segments

def time_to_str(seconds):
    """将秒数转换为 HH:MM:SS"""
    hours = int(seconds // 3600)
    remainder = seconds % 3600
    minutes = int(remainder // 60)
    seconds = int(remainder % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def process_video(input_path):
    """处理视频"""
    output_dir = os.path.join(os.path.dirname(input_path), "processed")
    os.makedirs(output_dir, exist_ok=True)

    # 获取视频信息
    total_duration = get_video_duration(input_path)
    total_time = time_to_str(total_duration)
    print(f"\n视频总时长：{total_time}")

    # 获取要删除的时间段
    cut_segments = get_cut_segments()
    if not cut_segments:
        print("错误：未输入任何时间段")
        sys.exit(1)

    # 验证时间段
    if not validate_segments(cut_segments, total_duration):
        sys.exit(1)

    # 生成保留时间段
    keep_segments = generate_keep_segments(cut_segments, total_duration)

    # 显示处理计划
    print("\n即将删除以下时间段：")
    for start, end, start_str, end_str in cut_segments:
        print(f"- {start_str} → {end_str}")

    print("\n保留以下时间段：")
    for start, end in keep_segments:
        print(f"- {time_to_str(start)} → {time_to_str(end)}")

    if input("\n确认处理？(y/n): ").lower() != 'y':
        print("操作已取消")
        sys.exit(0)

    # 分割保留片段
    temp_dir = os.path.join(output_dir, "temp")
    os.makedirs(temp_dir, exist_ok=True)
    
    part_files = []
    for idx, (start, end) in enumerate(keep_segments, 1):
        output_path = os.path.join(temp_dir, f"part{idx}.mp4")
        
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
            part_files.append(output_path)
            print(f"已生成保留片段 {idx}: {time_to_str(start)} → {time_to_str(end)}")
        except subprocess.CalledProcessError:
            print(f"错误：无法生成片段 {idx}")
            sys.exit(1)

    # 拼接视频
    final_output = os.path.join(output_dir, "final_output.mp4")
    
    # 生成文件列表
    list_file = os.path.join(temp_dir, "filelist.txt")
    with open(list_file, "w") as f:
        for file in part_files:
            f.write(f"file '{os.path.basename(file)}'\n")

    # 执行拼接
    cmd = [
        "ffmpeg",
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", list_file,
        "-c", "copy",
        final_output
    ]

    try:
        print("\n正在拼接视频...")
        subprocess.run(cmd, cwd=temp_dir, check=True, stderr=subprocess.DEVNULL)
        
        # 清理临时文件
        for file in part_files:
            os.remove(file)
        os.remove(list_file)
        os.rmdir(temp_dir)
        
        print(f"\n处理完成！最终视频：{final_output}")
    except subprocess.CalledProcessError:
        print("视频拼接失败")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        input("请将视频文件拖放到此窗口，按回车键退出...")
        sys.exit(1)
    
    video_path = sys.argv[1]
    if not os.path.isfile(video_path):
        input("错误：输入文件不存在，按回车键退出...")
        sys.exit(1)
    
    process_video(video_path)
    input("\n按回车键退出...")