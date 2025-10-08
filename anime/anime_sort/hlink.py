import os
import shutil

# ========== 配置区域 ==========
# 请根据需要修改以下配置

# 源文件夹路径
SOURCE_FOLDER = r"M:\downloads\sort"

# 目标文件夹路径
DESTINATION_FOLDER = r"M:\hlinks"

# 包含的文件扩展名（空列表表示包含所有类型）
INCLUDE_EXTENSIONS = [".mkv", ".mp4", ".ass"]  # 示例：只处理这些文件类型

# 排除的文件扩展名（空列表表示不排除任何类型）
EXCLUDE_EXTENSIONS = []  # 示例：排除这些文件类型

# 包含的文件夹名称（空列表表示包含所有文件夹）
INCLUDE_FOLDERS = []  # 示例：只处理这些文件夹

# 排除的文件夹名称（空列表表示不排除任何文件夹）
EXCLUDE_FOLDERS = ["CDs", "Scans"]  # 示例：排除这些文件夹

# 需要复制而不是创建硬链接的文件扩展名（空列表表示所有文件都创建硬链接）
COPY_EXTENSIONS = [".ass"]  # 示例：这些文件类型只复制，不创建硬链接

# 需要复制而不是创建硬链接的文件夹（空列表表示所有文件夹都创建硬链接）
COPY_FOLDERS = []  # 示例：这些文件夹中的文件只复制，不创建硬链接

# 排除小于指定大小的文件（单位：MB，0表示不排除任何文件）
EXCLUDE_SIZE_MB = 0  # 示例：排除小于1MB的文件

# 是否强制覆盖已存在的文件
FORCE_OVERWRITE = True

# ========== 脚本主体 ==========
# 以下代码不需要修改

def create_hard_link(src_path, dst_path):
    """创建硬链接"""
    try:
        # 如果目标文件已存在
        if os.path.exists(dst_path):
            if FORCE_OVERWRITE:
                # 强制覆盖：删除现有文件
                os.remove(dst_path)
            else:
                print(f"目标文件已存在，跳过: {dst_path}")
                return False
        
        # 创建硬链接
        os.link(src_path, dst_path)
        print(f"创建硬链接: {src_path} -> {dst_path}")
        return True
    except Exception as e:
        print(f"创建硬链接失败: {src_path} -> {dst_path}, 错误: {e}")
        # 如果硬链接失败（如跨文件系统），尝试复制文件
        try:
            shutil.copy2(src_path, dst_path)
            print(f"硬链接失败，改为复制: {src_path} -> {dst_path}")
            return True
        except Exception as copy_error:
            print(f"复制文件也失败: {src_path} -> {dst_path}, 错误: {copy_error}")
            return False

def copy_file(src_path, dst_path):
    """复制文件"""
    try:
        # 如果目标文件已存在
        if os.path.exists(dst_path):
            if FORCE_OVERWRITE:
                # 强制覆盖：删除现有文件
                os.remove(dst_path)
            else:
                print(f"目标文件已存在，跳过: {dst_path}")
                return False
        
        # 复制文件
        shutil.copy2(src_path, dst_path)
        print(f"复制文件: {src_path} -> {dst_path}")
        return True
    except Exception as e:
        print(f"复制文件失败: {src_path} -> {dst_path}, 错误: {e}")
        return False

def should_include_file(file_path):
    """判断是否应该包含该文件"""
    # 获取文件扩展名
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    
    # 检查文件大小 - 修改为排除小于指定大小的文件
    if EXCLUDE_SIZE_MB > 0:
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)  # 转换为MB
        if file_size_mb < EXCLUDE_SIZE_MB:  # 修改为小于
            return False
    
    # 检查包含扩展名
    if INCLUDE_EXTENSIONS and ext not in [e.lower() for e in INCLUDE_EXTENSIONS]:
        return False
    
    # 检查排除扩展名
    if EXCLUDE_EXTENSIONS and ext in [e.lower() for e in EXCLUDE_EXTENSIONS]:
        return False
    
    return True

def should_include_folder(folder_path):
    """判断是否应该包含该文件夹"""
    # 获取文件夹名称
    folder_name = os.path.basename(folder_path)
    
    # 检查包含文件夹
    if INCLUDE_FOLDERS and folder_name not in INCLUDE_FOLDERS:
        return False
    
    # 检查排除文件夹
    if EXCLUDE_FOLDERS and folder_name in EXCLUDE_FOLDERS:
        return False
    
    return True

def should_copy_file(file_path):
    """判断是否应该复制文件而不是创建硬链接"""
    # 获取文件扩展名和所在文件夹
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    folder_name = os.path.basename(os.path.dirname(file_path))
    
    # 检查扩展名是否需要复制
    if COPY_EXTENSIONS and ext in [e.lower() for e in COPY_EXTENSIONS]:
        return True
    
    # 检查文件夹是否需要复制
    if COPY_FOLDERS and folder_name in COPY_FOLDERS:
        return True
    
    return False

def process_files():
    """处理文件：创建硬链接或复制"""
    # 确保目标文件夹存在
    if not os.path.exists(DESTINATION_FOLDER):
        os.makedirs(DESTINATION_FOLDER)
    
    # 遍历源文件夹
    for root, dirs, files in os.walk(SOURCE_FOLDER):
        # 过滤文件夹
        dirs[:] = [d for d in dirs if should_include_folder(os.path.join(root, d))]
        
        # 计算相对于源文件夹的相对路径
        rel_path = os.path.relpath(root, SOURCE_FOLDER)
        dst_path = os.path.join(DESTINATION_FOLDER, rel_path)
        
        # 确保目标子文件夹存在
        if rel_path != "." and not os.path.exists(dst_path):
            os.makedirs(dst_path)
        
        # 处理文件
        for file in files:
            src_file_path = os.path.join(root, file)
            dst_file_path = os.path.join(dst_path, file)
            
            # 检查是否应该包含该文件
            if not should_include_file(src_file_path):
                continue
            
            # 判断是创建硬链接还是复制
            if should_copy_file(src_file_path):
                copy_file(src_file_path, dst_file_path)
            else:
                create_hard_link(src_file_path, dst_file_path)

def main():
    """主函数"""
    print("开始处理文件...")
    print(f"源文件夹: {SOURCE_FOLDER}")
    print(f"目标文件夹: {DESTINATION_FOLDER}")
    print(f"排除大小: 小于{EXCLUDE_SIZE_MB}MB的文件 ({'不排除任何文件' if EXCLUDE_SIZE_MB == 0 else f'排除小于{EXCLUDE_SIZE_MB}MB的文件'})")
    
    process_files()
    
    print("文件处理完成!")

if __name__ == "__main__":
    main()
