import subprocess
import sys
import os

# 支持转换的视频格式列表
SUPPORTED_EXTS = ['.mkv', '.avi', '.mov', '.flv', '.wmv', '.mpg', '.mpeg', '.m4v', '.webm']

def find_video_files(paths):
    """递归查找所有支持的视频文件"""
    video_files = []
    for path in paths:
        if os.path.isfile(path):
            if os.path.splitext(path)[1].lower() in SUPPORTED_EXTS:
                video_files.append(path)
        elif os.path.isdir(path):
            for root, _, files in os.walk(path):
                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    if ext in SUPPORTED_EXTS:
                        video_files.append(os.path.join(root, file))
    return video_files

def convert_to_mp4(input_path):
    """将单个视频转换为MP4容器格式"""
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_path = os.path.join(
        os.path.dirname(input_path),
        f"{base_name}.mp4"
    )

    # 跳过已存在的MP4文件
    if os.path.exists(output_path):
        print(f"跳过已存在文件：{os.path.basename(output_path)}")
        return

    cmd = [
        'ffmpeg',
        '-y',          # 覆盖输出文件
        '-i', input_path,
        '-c:v', 'copy', 
        '-c:a', 'copy',
        '-movflags', '+faststart',
        output_path
    ]
    
    try:
        print(f"正在转换：{os.path.basename(input_path)}")
        subprocess.run(cmd, check=True, stderr=subprocess.DEVNULL)
        print(f"✓ 转换成功：{os.path.basename(output_path)}\n")
    except subprocess.CalledProcessError as e:
        print(f"× 转换失败：{os.path.basename(input_path)} - {str(e)}\n")

def batch_convert(input_paths):
    """批量转换入口"""
    video_files = find_video_files(input_paths)
    
    if not video_files:
        print("未找到可转换的视频文件")
        return
    
    print(f"找到 {len(video_files)} 个待转换文件")
    for i, file in enumerate(video_files, 1):
        print(f"正在处理文件 ({i}/{len(video_files)})")
        convert_to_mp4(file)
    
    print("批量转换完成！")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        input("请将文件/文件夹拖放到此窗口，按回车键退出...")
        sys.exit(1)
    
    input_paths = sys.argv[1:]
    batch_convert(input_paths)
    input("\n按任意键退出...")