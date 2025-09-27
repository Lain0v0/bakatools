import os
import shutil

def get_file_names(folder):
    """
    获取文件夹中所有文件的文件名（不含扩展名）和完整文件名的映射
    
    参数:
    folder (str): 要扫描的文件夹路径
    
    返回:
    dict: 键为文件名（不含扩展名），值为完整文件名
    """
    # 创建字典，键为文件名（不含扩展名），值为完整文件名
    return {os.path.splitext(file)[0]: file for file in os.listdir(folder) if os.path.isfile(os.path.join(folder, file))}

def move_matching_files(source_folder, target_folder, destination_folder):
    """
    移动源文件夹中与目标文件夹中同名的文件到目标文件夹
    
    参数:
    source_folder (str): 源文件夹路径，包含要移动的文件
    target_folder (str): 目标文件夹路径，用于比较文件名
    destination_folder (str): 文件移动的目标位置
    """
    # 获取源文件夹和目标文件夹中的文件名映射
    source_files = get_file_names(source_folder)
    target_files = get_file_names(target_folder)
    
    # 如果目标文件夹不存在，则创建
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    
    # 遍历源文件夹中的所有文件
    for name, file in source_files.items():
        # 如果文件名（不含扩展名）在目标文件夹中存在
        if name in target_files:
            # 将文件从源文件夹移动到目标文件夹
            shutil.move(os.path.join(source_folder, file), os.path.join(destination_folder, file))
            print(f"Moved {file} to {destination_folder}")

if __name__ == "__main__":
    # 定义源文件夹路径（包含要移动的文件）
    source_folder = r"D:\Fonts\All\output"
    # 定义目标文件夹路径（用于比较文件名）
    target_folder = r"D:\Fonts\All\Fontworks\英文"
    # 定义文件移动的目标位置
    destination_folder = r"D:\Fonts\All\Fontworks\英文"
    
    # 执行文件移动操作
    move_matching_files(source_folder, target_folder, destination_folder)
