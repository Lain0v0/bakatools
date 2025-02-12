import subprocess
import sys
import os

def merge_videos(input_paths):
    """无损合并多个视频"""
    if len(input_paths) < 2:
        print("需要至少2个视频文件进行合并")
        return

    # 创建输出目录
    first_video = input_paths[0]
    base_dir = os.path.dirname(first_video)
    video_name = os.path.splitext(os.path.basename(first_video))[0]
    output_dir = os.path.join(base_dir, video_name)
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成文件列表
    temp_dir = os.path.join(output_dir, "merge_temp")
    os.makedirs(temp_dir, exist_ok=True)
    list_file = os.path.join(temp_dir, "filelist.txt")
    
    with open(list_file, "w", encoding="utf-8") as f:
        for path in input_paths:
            f.write(f"file '{os.path.abspath(path)}'\n")

    # 执行合并
    output_path = os.path.join(output_dir, f"{video_name}_merger.mp4")
    cmd = [
        "ffmpeg",
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", list_file,
        "-c", "copy",
        output_path
    ]

    try:
        subprocess.run(cmd, check=True)
        print(f"\n合并完成：{output_path}")
        
        # 清理临时文件
        os.remove(list_file)
        os.rmdir(temp_dir)
    except Exception as e:
        print(f"合并失败：{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        input("请将多个视频文件拖放到此窗口，按回车键退出...")
        sys.exit(1)
    
    input_paths = sys.argv[1:]
    merge_videos(input_paths)
    input("\n按回车键退出...")