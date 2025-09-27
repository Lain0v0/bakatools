import os
import shutil
import sys

def move_ass_files_and_folders(source_folders, exclusion_file, exclusion_folder):
    # 获取脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 使用相对路径创建.cache文件夹作为目标文件夹
    destination_folder = os.path.join(script_dir, ".cache")
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    # 先清空目标文件夹
    clear_destination_folder(destination_folder)
    
    for source_folder in source_folders:
        for root, dirs, files in os.walk(source_folder):
            # 移动包含"subsetted"的文件夹及其内容
            for dir_name in dirs:
                if exclusion_folder in dir_name:
                    source_dir_path = os.path.join(root, dir_name)
                    destination_dir_path = os.path.join(destination_folder, dir_name)
                    
                    # 如果目标文件夹已存在，先删除
                    if os.path.exists(destination_dir_path):
                        shutil.rmtree(destination_dir_path)
                    
                    shutil.move(source_dir_path, destination_dir_path)
                    print(f"Moved directory {source_dir_path} to {destination_dir_path}")

            # 移动不包含"assfonts"的.ass文件
            for file in files:
                if file.endswith(".ass") and exclusion_file not in os.path.splitext(file)[0]:
                    source_file_path = os.path.join(root, file)
                    destination_file_path = os.path.join(destination_folder, file)
                    
                    # 如果目标文件已存在，先删除
                    if os.path.exists(destination_file_path):
                        os.remove(destination_file_path)
                    
                    shutil.move(source_file_path, destination_file_path)
                    print(f"Moved {file} to {destination_folder}")

def clear_destination_folder(destination_folder):
    """清空目标文件夹中的所有内容"""
    if not os.path.exists(destination_folder):
        return
        
    for item in os.listdir(destination_folder):
        item_path = os.path.join(destination_folder, item)
        try:
            if os.path.isfile(item_path):
                os.remove(item_path)
                print(f"Deleted file: {item_path}")
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
                print(f"Deleted directory: {item_path}")
        except Exception as e:
            print(f"Error deleting {item_path}: {e}")
    
    print(f"Cleared destination folder: {destination_folder}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: move_ass_files.py <source_folders>...")
        sys.exit(1)

    source_folders = sys.argv[1:]
    exclusion_file = "assfonts"
    exclusion_folder = "subsetted"
    move_ass_files_and_folders(source_folders, exclusion_file, exclusion_folder)
