import subprocess
import sys
import os

def get_video_info(input_path):
    """获取视频基础信息"""
    cmd = [
        'ffprobe',
        '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height,duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        input_path
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        lines = result.stdout.strip().split('\n')
        if len(lines) != 3:
            print("错误：无法获取视频信息 - 输出格式不正确")
            sys.exit(1)
        width_str, height_str, duration_str = lines
        # 处理可能的N/A情况，例如某些视频可能没有持续时间
        try:
            width = int(width_str) if width_str != 'N/A' else 0
            height = int(height_str) if height_str != 'N/A' else 0
            duration = float(duration_str) if duration_str != 'N/A' else 0.0
        except ValueError:
            print("错误：无法解析视频信息")
            sys.exit(1)
        return width, height, duration
    except Exception as e:
        print(f"错误：无法获取视频信息 - {str(e)}")
        sys.exit(1)

def optimize_resolution(original_w, original_h):
    """优化输出分辨率"""
    max_width = 1280   # 限制最大宽度
    if original_w > max_width and original_w != 0:
        new_width = max_width
        if original_h == 0:
            new_height = 0
        else:
            new_height = int((max_width / original_w) * original_h)
        # 确保高度是偶数
        new_width -= (new_width % 2)
        new_height -= (new_height % 2)
        return new_width, new_height if new_height != 0 else max_width
    return original_w, original_h

def convert_to_mp4(input_path):
    """转换视频为高效MP4格式"""
    output_dir = os.path.join(os.path.dirname(input_path), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    filename = os.path.splitext(os.path.basename(input_path))[0]
    output_ath = os.path.join(output_dir, f"{filename}_optimized.mp4")

    # 使用ffprobe获取视频信息
    width, height, duration = get_video_info(input_path)

    if width == 0 or height == 0:
        print("错误：无法确定视频分辨率")
        return

    try:
        # 调整分辨率到合适的值，确保为偶数
        new_width, new_height = optimize_resolution(width, height)
        
        # 使用ffmpeg进行转码和调整分辨率
        ffmpeg_cmd = [
            'ffmpeg',
            '-i', input_path,
            '-vf', f'scale={new_width}:{new_height}',
            '-c:v', 'libx264',
            '-crf', '23',
            '-preset', 'fast',
            output_ath
        ]
        subprocess.run(ffmpeg_cmd, check=True)
        print(f"视频已成功转换为 {output_ath}")
    except subprocess.CalledProcessError as e:
        print(f"错误：视频转换失败 - {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python video2mp4.py <输入视频路径>")
        sys.exit(1)
    input_path = sys.argv[1]
    convert_to_mp4(input_path)