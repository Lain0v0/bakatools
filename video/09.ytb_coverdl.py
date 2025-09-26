import sys
import os
import requests
from urllib.parse import urlparse

def extract_video_id(url):
    """从YouTube图片URL中提取视频ID"""
    parsed = urlparse(url)
    path_segments = parsed.path.split('/')
    
    if len(path_segments) >= 4 and path_segments[1] == 'vi':
        return path_segments[2]
    return None

def download_image(url, save_dir):
    """下载并保存图片到指定目录"""
    video_id = extract_video_id(url)
    if not video_id:
        print(f"错误: 无法从URL提取视频ID - {url}")
        return False
    
    file_name = f"{video_id}.jpg"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        save_path = os.path.join(save_dir, file_name)
        with open(save_path, 'wb') as f:
            f.write(response.content)
        print(f"成功下载: {save_path}")
        return True
    except Exception as e:
        print(f"下载失败 - {url}: {str(e)}")
        return False

def read_urls_from_file(file_path):
    """从文本文件读取URL列表"""
    try:
        with open(file_path, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"读取文件失败: {str(e)}")
        return None

def main():
    if len(sys.argv) != 2:
        print("使用方法: python downloader.py <包含URL列表的txt文件>")
        sys.exit(1)

    input_file = sys.argv[1]
    
    # 获取保存目录（输入文件所在目录）
    save_dir = os.path.dirname(os.path.abspath(input_file))
    
    # 创建保存目录（如果不存在）
    os.makedirs(save_dir, exist_ok=True)
    
    # 读取URL列表
    urls = read_urls_from_file(input_file)
    if not urls:
        print("错误: 未找到有效URL或文件读取失败")
        sys.exit(1)
    
    # 下载所有图片
    success_count = 0
    for url in urls:
        if download_image(url, save_dir):
            success_count += 1
    
    print(f"\n下载完成，成功 {success_count}/{len(urls)} 个文件")

if __name__ == "__main__":
    main()