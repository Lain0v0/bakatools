import os
import shutil
import sys
import re

def rename_files(folder):
    for root, dirs, files in os.walk(folder):
        for file in files:
            new_name = file
            # 添加后缀
            if '1080p' in file:
                new_name = re.sub(r'(\.[^.]+)$', r' - 1080p\1', new_name)
            elif '720p' in file:
                new_name = re.sub(r'(\.[^.]+)$', r' - 720p\1', new_name)
            elif '2160p' in file:
                new_name = re.sub(r'(\.[^.]+)$', r' - 2160p\1', new_name)

            # 检测并替换 .JPSC 或 .SC 为 .zh-cn
            new_name = new_name.replace('.JPSC', '.zh-cn').replace('.SC', '.zh-cn')

            # 检测并替换 .JPTC 或 .TC 为 .zh-tw
            new_name = new_name.replace('.JPTC', '.zh-tw').replace('.TC', '.zh-tw')

            # 去除第一个和最后两个[]内的内容
            new_name = re.sub(r'\[.*?\]', '', new_name, count=1)
            new_name = re.sub(r'(.*)\[.*?\](.*)\[.*?\](.*)', r'\1\2\3', new_name)

            # 去除所有 [ 和 ]
            new_name = new_name.replace('[', '').replace(']', '')

            # 将两个连续的空格改为单个空格
            new_name = re.sub(r'\s\s+', ' ', new_name).strip()

            # 重命名文件
            os.rename(os.path.join(root, file), os.path.join(root, new_name))
            print(f'Renamed {file} to {new_name}')

def copy_and_move_files(folder, file_keywords, target_folder_name):
    for root, dirs, files in os.walk(folder):
        for file in files:
            if any(keyword.lower() in file.lower() for keyword in file_keywords):
                source_file_path = os.path.join(root, file)
                target_folder_path = os.path.join(folder, target_folder_name)
                if not os.path.exists(target_folder_path):
                    shutil.copytree(os.path.join(os.path.dirname(__file__), target_folder_name), target_folder_path)
                shutil.move(source_file_path, os.path.join(target_folder_path, file))
                print(f'Moved {file} to {target_folder_path}')
def add_trailer_suffix_to_pv_folder(pv_folder_path):
    """为PV文件夹中的mkv、mp4和ass文件添加-trailer后缀"""
    if not os.path.exists(pv_folder_path):
        return
    
    for filename in os.listdir(pv_folder_path):
        file_path = os.path.join(pv_folder_path, filename)
        if os.path.isfile(file_path):
            # 检查文件扩展名
            name, ext = os.path.splitext(filename)
            if ext.lower() in ['.mkv', '.mp4', '.ass']:
                # 检查是否已经包含-trailer后缀
                if not name.endswith('-trailer'):
                    new_name = f"{name}-trailer{ext}"
                    new_path = os.path.join(pv_folder_path, new_name)
                    
                    # 重命名文件
                    os.rename(file_path, new_path)
                    print(f'Added trailer suffix: {filename} -> {new_name}')
def process_files(source_folders):
    for source_folder in source_folders:
        rename_files(source_folder)
        copy_and_move_files(source_folder, ['PV', 'Preview'], 'PV')
        copy_and_move_files(source_folder, ['Menu'], 'Menus')
        copy_and_move_files(source_folder, ['NCOP', 'NCED'], 'OPED')
        copy_and_move_files(source_folder, ['IV', 'EVENT'], 'IV')
        copy_and_move_files(source_folder, ['CM'], 'CM')

        # 在所有移动操作完成后，为PV文件夹中的文件添加-trailer后缀
        pv_folder_path = os.path.join(source_folder, 'PV')
        add_trailer_suffix_to_pv_folder(pv_folder_path)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: detect_and_move.py <source_folders>...")
        sys.exit(1)

    source_folders = sys.argv[1:]
    process_files(source_folders)

