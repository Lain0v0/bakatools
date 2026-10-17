import os
import shutil
import sys
import re

# ============ 全局配置 ============

VIDEO_EXTS = {'.mkv', '.mp4', '.avi', '.mov', '.flv', '.wmv',
              '.webm', '.m4v', '.ts', '.m2ts'}

KEYWORD_CATEGORY = {
    'character pv': 'PV',
    'web preview':  'PV',
    'tv-spot':      'CM',
    'music video':  'IV',
    'nc-avant':     'OPED',
    'nc-apart':     'OPED',
    'nc-bpart':     'OPED',
    'ncop':         'OPED',
    'nced':         'OPED',
    'preview':      'PV',
    'trailer':      'PV',
    'teaser':       'PV',
    'spot':         'PV',
    'menu':         'Menu',
    'event':        'IV',
    'interview':    'IV',
    'making':       'IV',
    'stage':        'IV',
    'cm':           'CM',
    'mv':           'IV',
    'iv':           'IV',
    'pv':           'PV',
}

SEASON_NFO_TOP = {
    'PV': '''<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<season>
  <plot><![CDATA[宣传片、预告、角色 PV 等]]></plot>
  <outline><![CDATA[宣传片、预告、角色 PV 等]]></outline>
  <lockdata>true</lockdata>
  <title>PV</title>
  <sorttitle>PV</sorttitle>
  <seasonnumber>100</seasonnumber>
</season>
''',
    'OPED': '''<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<season>
  <plot><![CDATA[无字 OP/ED、无字开场片段等]]></plot>
  <outline><![CDATA[无字 OP/ED、无字开场片段等]]></outline>
  <lockdata>true</lockdata>
  <title>OPED</title>
  <sorttitle>OPED</sorttitle>
  <seasonnumber>101</seasonnumber>
</season>
''',
    'Menu': '''<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<season>
  <plot><![CDATA[Menu BD/DVD 播放选择菜单]]></plot>
  <outline><![CDATA[Menu BD/DVD 播放选择菜单]]></outline>
  <lockdata>true</lockdata>
  <dateadded>2024-10-31 14:08:04</dateadded>
  <title>菜单</title>
  <sorttitle>菜单</sorttitle>
  <seasonnumber>102</seasonnumber>
</season>
''',
    'CM': '''<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<season>
  <plot><![CDATA[电视放送广告]]></plot>
  <outline><![CDATA[电视放送广告]]></outline>
  <lockdata>true</lockdata>
  <title>广告</title>
  <sorttitle>广告</sorttitle>
  <seasonnumber>103</seasonnumber>
</season>
''',
    'IV': '''<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<season>
  <plot><![CDATA[访谈、舞台、制作花絮等三次元内容]]></plot>
  <outline><![CDATA[访谈、舞台、制作花絮等三次元内容]]></outline>
  <lockdata>true</lockdata>
  <title>真人特典</title>
  <sorttitle>真人特典</sorttitle>
  <seasonnumber>104</seasonnumber>
</season>
''',
    'Misc': '''<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<season>
  <plot><![CDATA[其他剩余特典]]></plot>
  <outline><![CDATA[其他剩余特典]]></outline>
  <lockdata>true</lockdata>
  <title>其他</title>
  <sorttitle>其他</sorttitle>
  <seasonnumber>105</seasonnumber>
</season>
''',
}

SEASON_NUM_MAP = {
    'PV':  100,
    'OPED': 101,
    'Menu': 102,
    'CM':  103,
    'IV':  104,
    'Misc': 105,
}

# 清晰度正则
QUALITY_PATTERN = re.compile(r'(2160p|1080p|720p|480p)', re.IGNORECASE)


# ============ 工具函数 ============

def parse_selection(s, max_n):
    """解析选择视频的输入"""
    result = []
    for part in re.split(r'[,\s]+', s.strip()):
        if not part:
            continue
        if '-' in part:
            a_s, b_s = part.split('-', 1)
            a, b = int(a_s), int(b_s)
            result.extend(range(a, b + 1))
        else:
            n = int(part)
            if 1 <= n <= max_n:
                result.append(n)
            else:
                for ch in part:
                    if not ch.isdigit():
                        raise ValueError(f"无效字符: {ch}")
                    result.append(int(ch))
    result = sorted(set(result))
    if not result or any(x < 1 or x > max_n for x in result):
        raise ValueError("选择超出范围")
    return result


def parse_ranges(s, max_n):
    """解析区间划分输入"""
    s = s.strip()
    if s == '0':
        return [(1, max_n)]
    ranges = []
    for part in re.split(r'[,\s]+', s):
        if not part:
            continue
        if '-' in part:
            a_s, b_s = part.split('-', 1)
            a, b = int(a_s), int(b_s)
        else:
            a = b = int(part)
        if a < 1 or b > max_n or a > b:
            raise ValueError(f"区间 {part} 无效")
        ranges.append((a, b))
    ranges.sort(key=lambda x: x[0])
    covered = set()
    for a, b in ranges:
        for i in range(a, b + 1):
            if i in covered:
                raise ValueError(f"区间 {a}-{b} 重叠")
            covered.add(i)
    if covered != set(range(1, max_n + 1)):
        raise ValueError("区间未覆盖全部已选文件")
    return ranges


def extract_quality(filename):
    m = QUALITY_PATTERN.search(filename)
    return m.group(1) if m else ''


def match_category(filename):
    name_lower = filename.lower()
    for kw, cat in sorted(KEYWORD_CATEGORY.items(), key=lambda x: -len(x[0])):
        if kw in name_lower:
            return cat
    return None


def add_quality_suffix_once(filename):
    """
    保证清晰度后缀（形如 ' - 1080p'）最多出现一次：
      - 文件名含清晰度标记才处理
      - 若扩展名前已有 ' - {quality}'，则不再添加
    """
    m = QUALITY_PATTERN.search(filename)
    if not m:
        return filename
    quality = m.group(1)
    name, ext = os.path.splitext(filename)
    # 已在主体中存在 ' - 1080p' 形态的清晰度后缀，不再重复添加
    if re.search(rf'\s-\s*{re.escape(quality)}(?![A-Za-z0-9])', name, re.IGNORECASE):
        return filename
    return f"{name} - {quality}{ext}"


# ============ 基础重命名 ============

def extract_folder_info(folder_path):
    folder_name = os.path.basename(folder_path)
    match = re.search(r'\](.*?)\[', folder_name)
    if match:
        content_a = match.group(1).strip()
        content_b = content_a.replace(' ', '+')
        print(f"TMDB搜索链接为：https://www.themoviedb.org/search?query={content_b}")
        return content_a
    return None


def get_user_input():
    while True:
        try:
            season_num = int(input("请问是动漫的第几季？"))
            break
        except ValueError:
            print("请输入有效的数字")
    season_str = str(season_num).zfill(2)

    while True:
        try:
            year_num = int(input("请问该季是几几年发布？"))
            if 1900 <= year_num <= 2100:
                break
            print("请输入合理的年份（1900-2100）")
        except ValueError:
            print("请输入有效的年份")

    chinese_name = input("动漫的中文名叫什么？")
    return season_str, year_num, chinese_name


def extract_first_bracket_content(folder_path):
    folder_name = os.path.basename(folder_path)
    match = re.search(r'\[(.*?)\]', folder_name)
    return match.group(1) if match else ""


def create_season_folder(folder_path, season_str, year_num, first_bracket_content):
    season_folder_name = f"Season {season_str} ({year_num}) [{first_bracket_content}]"
    season_folder_path = os.path.join(folder_path, season_folder_name)
    if not os.path.exists(season_folder_path):
        os.makedirs(season_folder_path)
        print(f"已创建文件夹: {season_folder_name}")
    return season_folder_path


def replace_chinese_name_in_files(folder_path, chinese_name):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            match = re.search(r'\](.*?)\[', file)
            if match:
                content_g = match.group(1).strip()
                new_filename = file.replace(content_g, f" {chinese_name} ")
                old_path = os.path.join(root, file)
                new_path = os.path.join(root, new_filename)
                if os.path.exists(new_path):
                    continue
                try:
                    os.rename(old_path, new_path)
                    print(f"已重命名: {file} -> {new_filename}")
                except OSError as e:
                    print(f"重命名失败: {file} -> {new_filename}: {e}")


def replace_episode_numbers_and_move(source_folder, season_folder_path, season_str):
    for file in os.listdir(source_folder):
        file_path = os.path.join(source_folder, file)
        if not os.path.isfile(file_path):
            continue
        matches = re.findall(r'\[(.*?)\]', file)
        if len(matches) >= 2:
            second_bracket = matches[1]
            if second_bracket.isdigit():
                number_h = second_bracket
                replacement = f"- S{season_str}E{number_h.zfill(2)}"
                new_filename = re.sub(r'\[(.*?)\]', replacement, file, count=2)
                new_filename = new_filename.replace(replacement, f"[{replacement}]", 1)

                old_path = os.path.join(source_folder, file)
                new_path = os.path.join(source_folder, new_filename)
                os.rename(old_path, new_path)
                print(f"已替换数字: {file} -> {new_filename}")

                shutil.move(new_path, os.path.join(season_folder_path, new_filename))
                print(f"已移动文件到: {season_folder_path}")
            else:
                shutil.move(file_path, os.path.join(season_folder_path, file))
                print(f"已移动文件到: {season_folder_path}")


def rename_files(folder):
    for root, dirs, files in os.walk(folder):
        for file in list(files):
            new_name = file

            # 清晰度后缀（只加一次）
            new_name = add_quality_suffix_once(new_name)

            # 语言标记
            new_name = new_name.replace('.JPSC', '.zh-cn').replace('.SC', '.zh-cn').replace('.CHS', '.zh-cn')
            new_name = new_name.replace('.jpsc', '.zh-cn').replace('.sc', '.zh-cn').replace('.chs', '.zh-cn')
            new_name = new_name.replace('.JPTC', '.zh-tw').replace('.TC', '.zh-tw').replace('.CHT', '.zh-tw')
            new_name = new_name.replace('.jptc', '.zh-tw').replace('.tc', '.zh-tw').replace('.cht', '.zh-tw')

            # 去除首尾括号
            new_name = re.sub(r'\[.*?\]', '', new_name, count=1)
            new_name = re.sub(r'(.*)\[.*?\](.*)\[.*?\](.*)', r'\1\2\3', new_name)
            new_name = new_name.replace('[', '').replace(']', '')
            new_name = re.sub(r'\s\s+', ' ', new_name).strip()

            # 语言标记移到扩展名前
            if '.zh-cn' in new_name or '.zh-tw' in new_name:
                name_without_ext, ext = os.path.splitext(new_name)
                if not (name_without_ext.endswith('.zh-cn') or name_without_ext.endswith('.zh-tw')):
                    if '.zh-cn' in name_without_ext:
                        name_without_zh = name_without_ext.replace('.zh-cn', '')
                        new_name = f"{name_without_zh}.zh-cn{ext}"
                    elif '.zh-tw' in name_without_ext:
                        name_without_zh = name_without_ext.replace('.zh-tw', '')
                        new_name = f"{name_without_zh}.zh-tw{ext}"

            old_path = os.path.join(root, file)
            new_path = os.path.join(root, new_name)
            if old_path == new_path:
                continue
            try:
                os.rename(old_path, new_path)
                print(f'已重命名: {file} -> {new_name}')
            except OSError as e:
                print(f'重命名失败: {file} -> {new_name}: {e}')


def process_season_folder(season_folder_path):
    print(f"开始处理Season文件夹: {season_folder_path}")
    rename_files(season_folder_path)


# ============ SPs 特别篇处理 ============

def rename_special_files(sps_dir, video_filename, chinese_name, episode_num, target_dir):
    video_base, video_ext = os.path.splitext(video_filename)
    quality = extract_quality(video_base)
    quality_part = f" - {quality}" if quality else ""
    new_base = f"{chinese_name} - S00E{episode_num:02d}{quality_part}"

    files_to_move = []
    for f in sorted(os.listdir(sps_dir)):
        src = os.path.join(sps_dir, f)
        if not os.path.isfile(src):
            continue
        if f == video_filename:
            files_to_move.append((f, video_ext))
        elif f.startswith(video_base + '.'):
            suffix = f[len(video_base):]
            files_to_move.append((f, suffix))

    for old_name, suffix in files_to_move:
        new_name = new_base + suffix
        src = os.path.join(sps_dir, old_name)
        dst = os.path.join(target_dir, new_name)
        if os.path.exists(dst):
            print(f"  目标已存在，跳过: {new_name}")
            continue
        shutil.move(src, dst)
        print(f"  已整理: {old_name} -> {new_name}")


def process_sp_specials(sps_folder_path, chinese_name):
    print("\n===== 特别篇处理 =====")
    video_files = [
        f for f in sorted(os.listdir(sps_folder_path))
        if os.path.isfile(os.path.join(sps_folder_path, f))
        and os.path.splitext(f)[1].lower() in VIDEO_EXTS
    ]
    if not video_files:
        print("SPs 根目录没有视频文件，跳过特别篇处理")
        return

    print("SPs 根目录中的视频文件：")
    for i, vf in enumerate(video_files, 1):
        print(f"  {i}. {vf}")

    while True:
        s = input("请选择对应 TMDB 特别篇的文件（如 1 / 1,2,5,6,8 / 1-10；输入 0 表示无特别篇跳过）：").strip()
        if s == '0':
            print("跳过特别篇处理")
            return
        try:
            selected_indices = parse_selection(s, len(video_files))
            break
        except Exception as e:
            print(f"输入有误: {e}，请重新输入")

    selected_files = [video_files[i - 1] for i in selected_indices]
    print("\n已选择的文件：")
    for i, f in enumerate(selected_files, 1):
        print(f"  {i}. {f}")

    while True:
        s = input(f"请划分区间（共 {len(selected_files)} 个文件，如 1-4,5-8；输入 0 表示全部为一个区间）：").strip()
        try:
            ranges = parse_ranges(s, len(selected_files))
            break
        except Exception as e:
            print(f"输入有误: {e}，请重新输入")

    while True:
        s = input(f"请输入 {len(ranges)} 个区间的起始集数（如 1,8,20）：").strip()
        try:
            starts = [int(x) for x in re.split(r'[,\s]+', s.strip()) if x]
            if len(starts) != len(ranges):
                raise ValueError(f"需要 {len(ranges)} 个数字")
            if any(x < 0 for x in starts):
                raise ValueError("集数不能为负")
            break
        except Exception as e:
            print(f"输入有误: {e}，请重新输入")

    file_episodes = {}
    for (a, b), ep_start in zip(ranges, starts):
        ep = ep_start
        for idx in range(a, b + 1):
            file_episodes[idx] = ep
            ep += 1

    season00_path = os.path.join(sps_folder_path, 'Season 00')
    os.makedirs(season00_path, exist_ok=True)

    for idx, vf in enumerate(selected_files, 1):
        ep = file_episodes.get(idx)
        if ep is None:
            print(f"警告: 文件 {vf} 未分配集数，跳过")
            continue
        print(f"\n处理: {vf} -> S00E{ep:02d}")
        rename_special_files(sps_folder_path, vf, chinese_name, ep, season00_path)

    print(f"\n特别篇已整理到: {season00_path}")


# ============ SPs 剩余分类 ============

def categorize_remaining_files(sps_folder_path):
    target_cats = {'PV', 'Menu', 'OPED', 'IV', 'CM', 'Misc', 'Season 00'}

    all_files = []
    for root, dirs, files in os.walk(sps_folder_path):
        if root == sps_folder_path:
            dirs[:] = [d for d in dirs if d not in target_cats]
        for f in files:
            all_files.append(os.path.join(root, f))

    for fp in all_files:
        if not os.path.isfile(fp):
            continue
        fn = os.path.basename(fp)
        cat = match_category(fn) or 'Misc'
        target_dir = os.path.join(sps_folder_path, cat)
        os.makedirs(target_dir, exist_ok=True)
        dst = os.path.join(target_dir, fn)
        if os.path.exists(dst):
            print(f"已存在，跳过: {fn}")
            continue
        shutil.move(fp, dst)
        print(f"已分类: {fn} -> {cat}")


# ============ 为 PV 加 -trailer ============

def add_trailer_suffix_to_pv_folder(pv_folder_path):
    if not os.path.exists(pv_folder_path):
        return
    for filename in os.listdir(pv_folder_path):
        fp = os.path.join(pv_folder_path, filename)
        if not os.path.isfile(fp):
            continue
        name, ext = os.path.splitext(filename)
        # 只处理含 PV 关键字的文件
        if 'pv' not in name.lower():
            continue
        if name.endswith('-trailer'):
            continue
        new_name = f"{name}-trailer{ext}"
        os.rename(fp, os.path.join(pv_folder_path, new_name))
        print(f"已添加trailer后缀: {filename} -> {new_name}")


# ============ 清理空文件夹 ============

def remove_empty_dirs(folder_path):
    for root, dirs, files in os.walk(folder_path, topdown=False):
        for d in dirs:
            dp = os.path.join(root, d)
            try:
                if not os.listdir(dp):
                    os.rmdir(dp)
                    print(f"已删除空文件夹: {dp}")
            except FileNotFoundError:
                pass


# ============ NFO 写入 ============

def add_season_nfo_files(sps_folder_path):
    for cat, content in SEASON_NFO_TOP.items():
        cat_path = os.path.join(sps_folder_path, cat)
        if not os.path.isdir(cat_path) or not os.listdir(cat_path):
            continue
        nfo_path = os.path.join(cat_path, 'season.nfo')
        with open(nfo_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"已写入: {nfo_path}")


def make_episode_nfo(title, season_num):
    return (
        '<?xml version="1.0" encoding="utf-8" standalone="yes"?>\n'
        '<episodedetails>\n'
        '  <plot />\n'
        '  <outline />\n'
        '  <lockdata>false</lockdata>\n'
        f'  <title>{title}</title>\n'
        f'  <sorttitle>{title}</sorttitle>\n'
        f'  <season>{season_num}</season>\n'
        '\n'
        '</episodedetails>\n'
    )


def add_episode_nfo_files(sps_folder_path):
    for cat, season_num in SEASON_NUM_MAP.items():
        cat_path = os.path.join(sps_folder_path, cat)
        if not os.path.isdir(cat_path):
            continue
        for filename in sorted(os.listdir(cat_path)):
            fp = os.path.join(cat_path, filename)
            if not os.path.isfile(fp):
                continue
            name, ext = os.path.splitext(filename)
            if ext.lower() not in VIDEO_EXTS:
                continue
            nfo_path = os.path.join(cat_path, f"{name}.nfo")
            with open(nfo_path, 'w', encoding='utf-8') as f:
                f.write(make_episode_nfo(name, season_num))
            print(f"已写入: {nfo_path}")


# ============ SPs 内容上移 ============

def move_sps_contents_up(sps_folder_path, folder_path):
    """把 SPs 里所有内容移到上级，返回冲突项"""
    conflicts = []
    for item in sorted(os.listdir(sps_folder_path)):
        src = os.path.join(sps_folder_path, item)
        dst = os.path.join(folder_path, item)
        if os.path.exists(dst):
            conflicts.append(item)
            print(f"目标已存在，跳过: {dst}")
            continue
        shutil.move(src, dst)
        print(f"已移动到上级: {item}")
    return conflicts


# ============ SPs 总流程 ============

def process_sps_folder(folder_path, chinese_name):
    sps_folder_path = os.path.join(folder_path, 'SPs')
    if not (os.path.exists(sps_folder_path) and os.path.isdir(sps_folder_path)):
        print("未找到 SPs 文件夹，跳过处理")
        return

    print(f"\n开始处理 SPs 文件夹: {sps_folder_path}")

    # 1) 通用重命名（清晰度后缀保证只有一个）
    rename_files(sps_folder_path)

    # 2) 处理特别篇
    process_sp_specials(sps_folder_path, chinese_name)

    # 3) 剩余文件分类
    categorize_remaining_files(sps_folder_path)

    # 4) PV 文件夹含 PV 关键字文件加 -trailer
    add_trailer_suffix_to_pv_folder(os.path.join(sps_folder_path, 'PV'))

    # 5) 删除空文件夹
    remove_empty_dirs(sps_folder_path)

    # 6) season.nfo
    add_season_nfo_files(sps_folder_path)

    # 7) episodedetails.nfo
    add_episode_nfo_files(sps_folder_path)

    # 8) 全部上移到上级
    conflicts = move_sps_contents_up(sps_folder_path, folder_path)

    # 9) 无冲突时删除 SPs，否则保留提示
    if conflicts:
        print(f"\n⚠️ 存在同名的目标，SPs 未删除，请手动检查: {sps_folder_path}")
        return

    if os.path.exists(sps_folder_path):
        remove_empty_dirs(sps_folder_path)
    if os.path.exists(sps_folder_path):
        shutil.rmtree(sps_folder_path)
        print(f"已删除 SPs 文件夹: {sps_folder_path}")


# ============ 主流程 ============

def process_folder(folder_path):
    extract_folder_info(folder_path)
    season_str, year_num, chinese_name = get_user_input()

    first_bracket_content = extract_first_bracket_content(folder_path)
    season_folder_path = create_season_folder(folder_path, season_str, year_num, first_bracket_content)

    replace_chinese_name_in_files(folder_path, chinese_name)
    replace_episode_numbers_and_move(folder_path, season_folder_path, season_str)
    process_season_folder(season_folder_path)
    process_sps_folder(folder_path, chinese_name)


def main():
    if len(sys.argv) < 2:
        print("用法: vcb_sort.py <源文件夹>...")
        sys.exit(1)

    if sys.argv[1:]:
        process_folder(sys.argv[1])


if __name__ == "__main__":
    main()