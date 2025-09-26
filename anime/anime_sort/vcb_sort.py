import os
import shutil
import sys
import re

def extract_folder_info(folder_path):
    """提取文件夹名中的信息"""
    folder_name = os.path.basename(folder_path)
    
    # 提取第一个"] ["之间的内容A
    pattern = r'\](.*?)\['
    match = re.search(pattern, folder_name)
    if match:
        content_a = match.group(1).strip()
        content_b = content_a.replace(' ', '+')
        print(f"TMDB搜索链接为：https://www.themoviedb.org/search?query={content_b}")
        return content_a
    return None

def get_user_input():
    """获取用户输入"""
    # 询问第几季
    while True:
        season_input = input("请问是动漫的第几季？")
        try:
            season_num = int(season_input)
            break
        except ValueError:
            print("请输入有效的数字")
    
    # 格式化季节数字
    season_str = str(season_num).zfill(2)
    
    # 询问发布年份
    while True:
        year_input = input("请问该季是几几年发布？")
        try:
            year_num = int(year_input)
            if 1900 <= year_num <= 2100:  # 合理的年份范围
                break
            else:
                print("请输入合理的年份（1900-2100）")
        except ValueError:
            print("请输入有效的年份")
    
    # 询问中文名
    chinese_name = input("动漫的中文名叫什么？")
    
    return season_str, year_num, chinese_name

def extract_first_bracket_content(folder_path):
    """提取文件夹名中第一个[]内的内容"""
    folder_name = os.path.basename(folder_path)
    pattern = r'\[(.*?)\]'
    match = re.search(pattern, folder_name)
    if match:
        return match.group(1)
    return ""

def create_season_folder(folder_path, season_str, year_num, first_bracket_content):
    """创建Season文件夹"""
    season_folder_name = f"Season {season_str} ({year_num}) [{first_bracket_content}]"
    season_folder_path = os.path.join(folder_path, season_folder_name)
    if not os.path.exists(season_folder_path):
        os.makedirs(season_folder_path)
        print(f"已创建文件夹: {season_folder_name}")
    return season_folder_path

def replace_chinese_name_in_files(folder_path, chinese_name):
    """将所有文件中的内容G替换为中文名"""
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            # 提取第一个"] ["之间的内容G
            pattern = r'\](.*?)\['
            match = re.search(pattern, file)
            if match:
                content_g = match.group(1).strip()
                new_filename = file.replace(content_g, f" {chinese_name} ")
                old_path = os.path.join(root, file)
                new_path = os.path.join(root, new_filename)
                os.rename(old_path, new_path)
                print(f"已重命名: {file} -> {new_filename}")

def replace_episode_numbers_and_move(source_folder, season_folder_path, season_str):
    """替换主文件夹下文件名中第二个[]内的数字，并移动到Season文件夹"""
    # 只处理主文件夹下的文件，不包括子文件夹
    for file in os.listdir(source_folder):
        file_path = os.path.join(source_folder, file)
        if os.path.isfile(file_path):
            # 找到所有[]的内容
            pattern = r'\[(.*?)\]'
            matches = re.findall(pattern, file)
            if len(matches) >= 2:
                # 提取第二个[]内的内容
                second_bracket = matches[1]
                # 检查是否为纯数字
                if second_bracket.isdigit():
                    number_h = second_bracket
                    replacement = f"- S{season_str}E{number_h.zfill(2)}"
                    new_filename = re.sub(r'\[(.*?)\]', replacement, file, count=2)
                    new_filename = new_filename.replace(replacement, f"[{replacement}]", 1)
                    
                    # 重命名文件
                    old_path = os.path.join(source_folder, file)
                    new_path = os.path.join(source_folder, new_filename)
                    os.rename(old_path, new_path)
                    print(f"已替换数字: {file} -> {new_filename}")
                    
                    # 移动文件到Season文件夹
                    shutil.move(new_path, os.path.join(season_folder_path, new_filename))
                    print(f"已移动文件到: {season_folder_path}")
                else:
                    # 如果不是纯数字，直接移动到Season文件夹
                    shutil.move(file_path, os.path.join(season_folder_path, file))
                    print(f"已移动文件到: {season_folder_path}")

def rename_files(folder):
    """重命名文件（原有功能）"""
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
            new_name = new_name.replace('.JPSC', '.zh-cn').replace('.SC', '.zh-cn').replace('.CHS', '.zh-cn')
            new_name = new_name.replace('.jpsc', '.zh-cn').replace('.sc', '.zh-cn').replace('.chs', '.zh-cn')
            
            # 检测并替换 .JPTC 或 .TC 为 .zh-tw
            new_name = new_name.replace('.JPTC', '.zh-tw').replace('.TC', '.zh-tw').replace('.CHT', '.zh-tw')
            new_name = new_name.replace('.jptc', '.zh-tw').replace('.tc', '.zh-tw').replace('.cht', '.zh-tw')
            
            # 去除第一个和最后两个[]内的内容
            new_name = re.sub(r'\[.*?\]', '', new_name, count=1)
            new_name = re.sub(r'(.*)\[.*?\](.*)\[.*?\](.*)', r'\1\2\3', new_name)

            # 去除所有 [ 和 ]
            new_name = new_name.replace('[', '').replace(']', '')

            # 将两个连续的空格改为单个空格
            new_name = re.sub(r'\s\s+', ' ', new_name).strip()

            # 将.zh-cn和.zh-tw移动到文件名末尾，文件扩展名之前
            if '.zh-cn' in new_name or '.zh-tw' in new_name:
                # 分离文件名和扩展名
                name_without_ext, ext = os.path.splitext(new_name)
                
                # 检查是否已经有语言标记在末尾
                if name_without_ext.endswith('.zh-cn') or name_without_ext.endswith('.zh-tw'):
                    # 已经在末尾，不需要移动
                    pass
                else:
                    # 查找语言标记的位置
                    zh_cn_pos = name_without_ext.find('.zh-cn')
                    zh_tw_pos = name_without_ext.find('.zh-tw')
                    
                    if zh_cn_pos != -1:
                        # 移除语言标记
                        name_without_zh = name_without_ext.replace('.zh-cn', '')
                        # 将语言标记添加到末尾
                        new_name_without_ext = f"{name_without_zh}.zh-cn"
                        new_name = f"{new_name_without_ext}{ext}"
                    elif zh_tw_pos != -1:
                        # 移除语言标记
                        name_without_zh = name_without_ext.replace('.zh-tw', '')
                        # 将语言标记添加到末尾
                        new_name_without_ext = f"{name_without_zh}.zh-tw"
                        new_name = f"{new_name_without_ext}{ext}"
         
            # 重命名文件
            os.rename(os.path.join(root, file), os.path.join(root, new_name))
            print(f'Renamed {file} to {new_name}')

def copy_and_move_files(folder, file_keywords, target_folder_name):
    """移动文件到指定文件夹，如果目标文件夹不存在则从模板复制"""
    # 获取脚本所在目录的路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 构建目标文件夹路径和模板文件夹路径
    target_folder_path = os.path.join(folder, target_folder_name)
    template_folder_path = os.path.join(script_dir, target_folder_name)
    
    # 如果目标文件夹不存在，从模板文件夹复制整个结构
    if not os.path.exists(target_folder_path):
        if os.path.exists(template_folder_path) and os.path.isdir(template_folder_path):
            # 复制整个模板文件夹及其内容
            shutil.copytree(template_folder_path, target_folder_path)
            print(f"已从模板复制文件夹: {target_folder_name}")
        else:
            # 如果模板文件夹不存在，只创建空的目标文件夹
            os.makedirs(target_folder_path)
            print(f"已创建空文件夹: {target_folder_name}")
    
    # 然后移动匹配的文件
    for root, dirs, files in os.walk(folder):
        for file in files:
            # 跳过目标文件夹中的文件，避免重复移动
            if root.startswith(target_folder_path):
                continue
                
            if any(keyword.lower() in file.lower() for keyword in file_keywords):
                source_file_path = os.path.join(root, file)
                shutil.move(source_file_path, os.path.join(target_folder_path, file))
                print(f'Moved {file} to {target_folder_path}')

def add_trailer_suffix_to_pv_folder(pv_folder_path):
    """为PV文件夹中的mkv、mp4和ass文件添加-trailer后缀（原有功能）"""
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

def process_season_folder(season_folder_path):
    """处理Season文件夹（原有功能）"""
    print(f"开始处理Season文件夹: {season_folder_path}")
    rename_files(season_folder_path)

def cleanup_empty_folders(folder_path):
    """清理空文件夹，除了season.nfo文件"""
    for root, dirs, files in os.walk(folder_path, topdown=False):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            # 检查文件夹是否只包含season.nfo文件
            contents = os.listdir(dir_path)
            if len(contents) == 1 and contents[0] == 'season.nfo':
                # 删除season.nfo文件
                season_nfo_path = os.path.join(dir_path, 'season.nfo')
                os.remove(season_nfo_path)
                print(f"已删除文件: {season_nfo_path}")
            
            # 再次检查文件夹是否为空
            if not os.listdir(dir_path):
                os.rmdir(dir_path)
                print(f"已删除空文件夹: {dir_path}")

def process_sps_folder(folder_path):
    """处理SPs子文件夹（原有功能）"""
    sps_folder_path = os.path.join(folder_path, 'SPs')
    if os.path.exists(sps_folder_path) and os.path.isdir(sps_folder_path):
        print(f"开始处理SPs文件夹: {sps_folder_path}")
        rename_files(sps_folder_path)
        copy_and_move_files(sps_folder_path, ['PV', 'Preview'], 'PV')
        copy_and_move_files(sps_folder_path, ['Menu'], 'Menus')
        copy_and_move_files(sps_folder_path, ['NCOP', 'NCED'], 'OPED')
        copy_and_move_files(sps_folder_path, ['IV', 'EVENT'], 'IV')
        copy_and_move_files(sps_folder_path, ['CM'], 'CM')

        # 在所有移动操作完成后，为PV文件夹中的文件添加-trailer后缀
        pv_folder_path = os.path.join(sps_folder_path, 'PV')
        add_trailer_suffix_to_pv_folder(pv_folder_path)
        
        # 清理空文件夹（包括只包含season.nfo的文件夹）
        cleanup_empty_folders(sps_folder_path)
        
        # 检查SPs文件夹是否为空，如果为空则删除
        if not os.listdir(sps_folder_path):
            os.rmdir(sps_folder_path)
            print(f"已删除空的SPs文件夹: {sps_folder_path}")
    else:
        print("未找到SPs文件夹，跳过处理")

def process_folder(folder_path):
    """处理单个文件夹"""
    # 1. 提取文件夹名信息并输出TMDB链接
    content_a = extract_folder_info(folder_path)
    
    # 2-4. 获取用户输入
    season_str, year_num, chinese_name = get_user_input()
    
    # 5. 提取第一个[]内的内容F并创建Season文件夹
    first_bracket_content = extract_first_bracket_content(folder_path)
    season_folder_path = create_season_folder(folder_path, season_str, year_num, first_bracket_content)
    
    # 6. 替换所有文件中第一个"] ["内的内容G为中文名
    replace_chinese_name_in_files(folder_path, chinese_name)
    
    # 7. 替换主文件夹下文件名中第二个[]内的数字，并移动到Season文件夹
    replace_episode_numbers_and_move(folder_path, season_folder_path, season_str)
    
    # 8. 处理Season文件夹（原有功能）
    process_season_folder(season_folder_path)
    
    # 9. 处理SPs子文件夹
    process_sps_folder(folder_path)

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("Usage: detect_and_move.py <source_folders>...")
        sys.exit(1)

    source_folders = sys.argv[1:]
    
    # 只处理第一个拖入的文件夹
    if source_folders:
        process_folder(source_folders[0])

if __name__ == "__main__":
    main()
