#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import json
import subprocess
import platform
from datetime import datetime
import webbrowser
import http.server
import socketserver
import threading
import sys
import time
import urllib.parse
from pathlib import Path

def find_cover_image(folder_path):
    """在文件夹中查找封面图片"""
    cover_names = ['folder', 'cover', 'thumbnail', 'preview', 'thumb', 'image']
    image_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp', '.tiff']
    
    # 获取所有图片文件
    image_files = []
    for file in sorted(os.listdir(folder_path)):
        if os.path.isfile(os.path.join(folder_path, file)):
            file_lower = file.lower()
            name, ext = os.path.splitext(file_lower)
            
            if ext in image_extensions:
                # 检查是否是指定的封面文件名
                if any(cover_name == name for cover_name in cover_names):
                    return file
                image_files.append(file)
    
    # 如果没有找到特定封面，返回第一个图片文件
    return image_files[0] if image_files else None

def scan_directory(base_dir):
    """扫描目录并返回分类数据"""
    categories = {}
    
    print(f"📁 Scanning directory: {os.path.abspath(base_dir)}")
    
    # 获取所有子文件夹（第一层）
    for item in sorted(os.listdir(base_dir)):
        item_path = os.path.join(base_dir, item)
        
        if os.path.isdir(item_path):
            category_name = item
            category_items = []
            
            print(f"  📂 Category: {category_name}")
            
            # 扫描该文件夹内的项目
            for subitem in sorted(os.listdir(item_path)):
                subitem_path = os.path.join(item_path, subitem)
                
                if os.path.isdir(subitem_path):
                    cover_image = find_cover_image(subitem_path)
                    
                    if cover_image:
                        category_items.append({
                            'name': subitem,
                            'cover': urllib.parse.quote(f"{category_name}/{subitem}/{cover_image}"),
                            'path': subitem_path,
                            'category': category_name,
                            'cover_file': cover_image
                        })
                    else:
                        # 没有封面图的文件夹也显示
                        category_items.append({
                            'name': subitem,
                            'cover': 'no_image.png',
                            'path': subitem_path,
                            'category': category_name,
                            'cover_file': None
                        })
            
            if category_items:
                categories[category_name] = category_items
                print(f"    ✅ Found {len(category_items)} items")
    
    return categories

def open_folder(path):
    """打开文件夹（跨平台）"""
    try:
        if platform.system() == "Windows":
            # Windows
            os.startfile(path)
            return True
        elif platform.system() == "Darwin":
            # macOS
            subprocess.run(["open", path], check=True)
            return True
        else:
            # Linux
            subprocess.run(["xdg-open", path], check=True)
            return True
    except Exception as e:
        print(f"⚠️ Could not open folder: {e}")
        return False

def create_default_image():
    """创建默认图片（如果没有的话）"""
    default_image = "no_image.png"
    if not os.path.exists(default_image):
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # 创建暗色背景的默认图片
            img = Image.new('RGB', (256, 256), color=(40, 40, 40))
            draw = ImageDraw.Draw(img)
            
            # 添加图标和文字
            # 绘制一个简单的文件夹图标
            draw.rectangle([80, 80, 176, 176], fill=(60, 60, 60), outline=(100, 100, 100))
            draw.rectangle([96, 96, 160, 160], fill=(80, 80, 80))
            
            # 添加文字
            try:
                font = ImageFont.truetype("arial.ttf", 20)
            except:
                font = ImageFont.load_default()
            
            draw.text((128, 200), "No Image", fill=(180, 180, 180), anchor="mm", font=font)
            
            img.save(default_image)
            print(f"📷 Created default image: {default_image}")
        except ImportError:
            # 如果没有PIL，创建一个简单的占位符
            print("⚠️ Install Pillow for better default image: pip install Pillow")
            # 创建一个简单的PNG文件头（最小有效的PNG）
            with open(default_image, 'wb') as f:
                # 这是一个1x1的黑色PNG
                f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x00\r\x0c\x08\x00\x00\x00\x00IEND\xaeB`\x82')
    
    return default_image

def generate_html(categories, output_file='gallery.html', lang='en-US'):
    """生成HTML文件"""
    
    # 多语言文本
    translations = {
        'zh-CN': {
            'title': '资源图库',
            'search_placeholder': '搜索项目名称...',
            'total_categories': '分类数量',
            'total_items': '项目总数',
            'showing': '显示中',
            'last_updated': '最后更新',
            'no_results': '未找到匹配的项目',
            'click_to_open': '点击打开文件夹',
            'open_folder': '打开文件夹',
            'all': '全部',
            'generated_on': '生成于',
            'categories': '个分类',
            'items': '个项目',
            'view_all': '全部项目',
            'filter_by_category': '按分类筛选',
            'stats': '统计信息'
        },
        'ja-JP': {
            'title': 'リソースギャラリー',
            'search_placeholder': 'アイテム名を検索...',
            'total_categories': 'カテゴリー数',
            'total_items': 'アイテム総数',
            'showing': '表示中',
            'last_updated': '最終更新',
            'no_results': '該当するアイテムが見つかりません',
            'click_to_open': 'クリックでフォルダを開く',
            'open_folder': 'フォルダを開く',
            'all': '全て',
            'generated_on': '生成日',
            'categories': 'カテゴリー',
            'items': 'アイテム',
            'view_all': '全アイテム表示',
            'filter_by_category': 'カテゴリーでフィルター',
            'stats': '統計情報'
        },
        'ko-KR': {
            'title': 'リソース 갤러리',
            'search_placeholder': '아이템 이름 검색...',
            'total_categories': '카테고리 수',
            'total_items': '총 아이템 수',
            'showing': '표시 중',
            'last_updated': '마지막 업데이트',
            'no_results': '일치하는 항목을 찾을 수 없습니다',
            'click_to_open': '클릭하여 폴더 열기',
            'open_folder': '폴더 열기',
            'all': '전체',
            'generated_on': '생성일',
            'categories': '카테고리',
            'items': '아이템',
            'view_all': '전체 아이템 보기',
            'filter_by_category': '카테ゴ리별 필터',
            'stats': '통계 정보'
        },
        'en-US': {
            'title': 'Resource Gallery',
            'search_placeholder': 'Search item name...',
            'total_categories': 'Categories',
            'total_items': 'Total Items',
            'showing': 'Showing',
            'last_updated': 'Last Updated',
            'no_results': 'No matching items found',
            'click_to_open': 'Click to open folder',
            'open_folder': 'Open Folder',
            'all': 'All',
            'generated_on': 'Generated on',
            'categories': 'categories',
            'items': 'items',
            'view_all': 'View All Items',
            'filter_by_category': 'Filter by Category',
            'stats': 'Statistics'
        }
    }
    
    t = translations.get(lang, translations['en-US'])
    
    # 创建默认图片
    default_image = create_default_image()
    
    # 计算总数
    total_items = sum(len(items) for items in categories.values())
    total_categories = len(categories)
    
    # 获取当前时间
    current_time = datetime.now()
    
    # 生成HTML内容 - 使用简单的字符串拼接避免复杂的f-string嵌套
    html_parts = []
    
    # HTML头部
    html_parts.append(f'''<!DOCTYPE html>
<html lang="{lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{t['title']} - {total_categories} {t['categories']}, {total_items} {t['items']}</title>
    <style>
        :root {{
            --bg-primary: #121212;
            --bg-secondary: #1e1e1e;
            --bg-card: #2d2d2d;
            --bg-tab: #252525;
            --text-primary: #ffffff;
            --text-secondary: #b0b0b0;
            --text-muted: #808080;
            --accent: #4a9eff;
            --accent-hover: #5aa8ff;
            --border: #3a3a3a;
            --border-light: #4a4a4a;
            --shadow: rgba(0, 0, 0, 0.4);
            --shadow-light: rgba(0, 0, 0, 0.2);
            --success: #10b981;
            --warning: #f59e0b;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 
                       'Noto Sans SC', 'Hiragino Sans GB', 'Microsoft YaHei', 
                       'Noto Sans CJK KR', sans-serif;
            background-color: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1800px;
            margin: 0 auto;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding: 25px;
            background: var(--bg-secondary);
            border-radius: 12px;
            border: 1px solid var(--border);
            box-shadow: 0 4px 12px var(--shadow);
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            margin-bottom: 10px;
            background: linear-gradient(45deg, var(--accent), var(--accent-hover));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .header p {{
            color: var(--text-secondary);
            margin-bottom: 20px;
        }}
        
        .stats-container {{
            display: flex;
            justify-content: center;
            gap: 30px;
            margin: 20px 0;
            flex-wrap: wrap;
        }}
        
        .stat-box {{
            background: var(--bg-card);
            padding: 20px;
            border-radius: 10px;
            border: 1px solid var(--border);
            min-width: 150px;
            text-align: center;
        }}
        
        .stat-number {{
            font-size: 2.5rem;
            font-weight: bold;
            color: var(--accent);
            display: block;
            line-height: 1;
        }}
        
        .stat-label {{
            font-size: 0.9rem;
            color: var(--text-secondary);
            margin-top: 10px;
        }}
        
        .controls {{
            display: flex;
            gap: 15px;
            margin: 25px 0;
            align-items: center;
            justify-content: center;
            flex-wrap: wrap;
        }}
        
        .search-box {{
            flex: 1;
            max-width: 400px;
            padding: 12px 20px;
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 8px;
            color: var(--text-primary);
            font-size: 1rem;
            outline: none;
            transition: all 0.2s;
        }}
        
        .search-box:focus {{
            border-color: var(--accent);
            box-shadow: 0 0 0 2px rgba(74, 158, 255, 0.2);
        }}
        
        .language-switcher {{
            display: flex;
            gap: 8px;
            background: var(--bg-card);
            padding: 8px;
            border-radius: 8px;
            border: 1px solid var(--border);
        }}
        
        .lang-btn {{
            padding: 6px 12px;
            background: transparent;
            border: 1px solid transparent;
            border-radius: 6px;
            color: var(--text-secondary);
            cursor: pointer;
            transition: all 0.2s;
            font-size: 0.9rem;
        }}
        
        .lang-btn:hover {{
            background: var(--bg-secondary);
        }}
        
        .lang-btn.active {{
            background: var(--accent);
            color: white;
            border-color: var(--accent);
        }}
        
        .category-tabs {{
            display: flex;
            gap: 10px;
            margin: 20px 0;
            padding: 0 10px;
            flex-wrap: wrap;
            justify-content: center;
        }}
        
        .category-tab {{
            padding: 10px 20px;
            background: var(--bg-tab);
            border: 1px solid var(--border);
            border-radius: 8px;
            color: var(--text-secondary);
            cursor: pointer;
            transition: all 0.2s;
            font-weight: 500;
            white-space: nowrap;
        }}
        
        .category-tab:hover {{
            background: var(--bg-secondary);
            transform: translateY(-2px);
        }}
        
        .category-tab.active {{
            background: var(--accent);
            color: white;
            border-color: var(--accent);
            box-shadow: 0 4px 12px rgba(74, 158, 255, 0.3);
        }}
        
        .category-tab .count {{
            background: rgba(0, 0, 0, 0.3);
            padding: 2px 6px;
            border-radius: 10px;
            font-size: 0.8rem;
            margin-left: 5px;
        }}
        
        .card-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 25px;
            padding: 20px 0;
            opacity: 0;
            animation: fadeIn 0.5s forwards;
        }}
        
        @keyframes fadeIn {{
            to {{ opacity: 1; }}
        }}
        
        .card {{
            background: var(--bg-card);
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid var(--border);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            cursor: pointer;
            position: relative;
        }}
        
        .card:hover {{
            transform: translateY(-8px);
            border-color: var(--accent);
            box-shadow: 0 12px 30px var(--shadow);
        }}
        
        .card-image {{
            width: 100%;
            height: 300px;
            object-fit: cover;
            display: block;
            background: var(--bg-secondary);
        }}
        
        .card-content {{
            padding: 20px;
        }}
        
        .card-title {{
            font-weight: 600;
            margin-bottom: 8px;
            font-size: 1.1rem;
            line-height: 1.4;
            overflow: hidden;
            text-overflow: ellipsis;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
        }}
        
        .card-category {{
            font-size: 0.85rem;
            color: var(--accent);
            font-weight: 500;
            margin-bottom: 5px;
        }}
        
        .card-path {{
            font-size: 0.8rem;
            color: var(--text-secondary);
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            font-family: 'SF Mono', 'Consolas', monospace;
        }}
        
        .card-hint {{
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            background: rgba(0, 0, 0, 0.8);
            padding: 8px;
            text-align: center;
            font-size: 0.85rem;
            color: var(--text-primary);
            opacity: 0;
            transition: opacity 0.2s;
        }}
        
        .card:hover .card-hint {{
            opacity: 1;
        }}
        
        .no-image {{
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--text-secondary);
            font-size: 0.9rem;
            height: 300px;
        }}
        
        .no-results {{
            text-align: center;
            padding: 60px 20px;
            grid-column: 1 / -1;
            color: var(--text-secondary);
            font-size: 1.1rem;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid var(--border);
            color: var(--text-secondary);
            font-size: 0.9rem;
        }}
        
        .active-category-title {{
            text-align: center;
            margin: 20px 0;
            color: var(--text-primary);
            font-size: 1.5rem;
            font-weight: 500;
        }}
        
        .active-category-title span {{
            color: var(--accent);
            font-weight: 600;
        }}
        
        @media (max-width: 768px) {{
            .card-grid {{
                grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
                gap: 15px;
            }}
            
            .header h1 {{
                font-size: 2rem;
            }}
            
            .stats-container {{
                gap: 15px;
            }}
            
            .stat-box {{
                min-width: 120px;
                padding: 15px;
            }}
            
            .category-tabs {{
                padding: 0 5px;
            }}
            
            .category-tab {{
                padding: 8px 15px;
                font-size: 0.9rem;
            }}
        }}
        
        @media (max-width: 480px) {{
            .card-grid {{
                grid-template-columns: 1fr;
            }}
            
            .controls {{
                flex-direction: column;
            }}
            
            .search-box {{
                max-width: 100%;
            }}
            
            .language-switcher {{
                width: 100%;
                justify-content: center;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎨 {t['title']}</h1>
            <p>{t['generated_on']}: {current_time.strftime("%Y-%m-%d %H:%M")}</p>
            
            <div class="language-switcher">
                <button class="lang-btn active" data-lang="en-US">English</button>
                <button class="lang-btn" data-lang="zh-CN">中文</button>
                <button class="lang-btn" data-lang="ja-JP">日本語</button>
                <button class="lang-btn" data-lang="ko-KR">한국어</button>
            </div>
            
            <div class="controls">
                <input type="text" class="search-box" id="searchInput" placeholder="{t['search_placeholder']}">
            </div>
            
            <div class="stats-container">
                <div class="stat-box">
                    <span class="stat-number" id="categoryCount">{total_categories}</span>
                    <span class="stat-label">{t['total_categories']}</span>
                </div>
                <div class="stat-box">
                    <span class="stat-number" id="totalCount">{total_items}</span>
                    <span class="stat-label">{t['total_items']}</span>
                </div>
                <div class="stat-box">
                    <span class="stat-number" id="showingCount">0</span>
                    <span class="stat-label">{t['showing']}</span>
                </div>
                <div class="stat-box">
                    <span class="stat-number">{current_time.strftime("%Y-%m-%d")}</span>
                    <span class="stat-label">{t['last_updated']}</span>
                </div>
            </div>
        </div>
        
        <div class="active-category-title" id="activeCategoryTitle">
            {t['view_all']} (<span>{total_items}</span> {t['items']})
        </div>
        
        <div class="category-tabs" id="categoryTabs">
            <!-- Category tabs will be generated by JavaScript -->
        </div>
        
        <div class="card-grid" id="cardContainer">
            <!-- Cards will be generated by JavaScript -->
        </div>
        
        <div class="footer">
            <p>{t['title']} | {total_categories} {t['categories']} | {total_items} {t['items']} | © {current_time.year}</p>
        </div>
    </div>
''')
    
    # JavaScript部分 - 使用转义处理
    html_parts.append(f'''
    <script>
        // Global data
        const allCategories = {json.dumps(categories, ensure_ascii=False)};
        const translations = {json.dumps(translations, ensure_ascii=False)};
        let currentLang = '{lang}';
        let activeCategory = 'all';
        
        // Flatten all items for search
        const allItems = [];
        Object.entries(allCategories).forEach(([category, items]) => {{
            items.forEach(item => {{
                item.category = category;
                allItems.push(item);
            }});
        }});
        
        // Initialize
        function init() {{
            renderCategoryTabs();
            renderItems(allItems);
            setupEventListeners();
            updateLanguage(currentLang);
            updateStats();
        }}
        
        // Render category tabs
        function renderCategoryTabs() {{
            const tabsContainer = document.getElementById('categoryTabs');
            tabsContainer.innerHTML = '';
            
            // All tab
            const allTab = document.createElement('div');
            allTab.className = 'category-tab active';
            allTab.dataset.category = 'all';
            allTab.innerHTML = `{t['all']} <span class="count">${{allItems.length}}</span>`;
            allTab.addEventListener('click', () => switchCategory('all'));
            tabsContainer.appendChild(allTab);
            
            // Category tabs
            Object.entries(allCategories).forEach(([category, items]) => {{
                const tab = document.createElement('div');
                tab.className = 'category-tab';
                tab.dataset.category = category;
                tab.innerHTML = `${{category}} <span class="count">${{items.length}}</span>`;
                tab.addEventListener('click', () => switchCategory(category));
                tabsContainer.appendChild(tab);
            }});
        }}
        
        // Switch category
        function switchCategory(category) {{
            activeCategory = category;
            
            // Update active tab
            document.querySelectorAll('.category-tab').forEach(tab => {{
                tab.classList.toggle('active', tab.dataset.category === category);
            }});
            
            // Update category title
            const titleElement = document.getElementById('activeCategoryTitle');
            const t = translations[currentLang];
            
            if (category === 'all') {{
                titleElement.innerHTML = `${{t.view_all}} (<span>${{allItems.length}}</span> ${{t.items.toLowerCase()}})`;
            }} else {{
                const count = allCategories[category].length;
                titleElement.innerHTML = `<span>${{category}}</span> - ${{count}} ${{t.items.toLowerCase()}}`;
            }}
            
            // Filter and render items
            const searchTerm = document.getElementById('searchInput').value.toLowerCase();
            filterItems(searchTerm);
        }}
        
        // Render items
        function renderItems(items) {{
            const container = document.getElementById('cardContainer');
            container.innerHTML = '';
            
            if (items.length === 0) {{
                const t = translations[currentLang];
                container.innerHTML = `<div class="no-results">${{t.no_results}}</div>`;
                return;
            }}
            
            items.forEach(item => {{
                const card = document.createElement('div');
                card.className = 'card';
                card.dataset.name = item.name.toLowerCase();
                card.dataset.category = item.category;
                
                const imageSrc = item.cover === 'no_image.png' ? '{default_image}' : decodeURIComponent(item.cover);
                
                card.innerHTML = `
                    <img src="${{imageSrc}}" alt="${{item.name}}" class="card-image" loading="lazy" 
                         onerror="this.onerror=null; this.src='{default_image}';">
                    <div class="card-content">
                        <div class="card-category">${{item.category}}</div>
                        <div class="card-title">${{item.name}}</div>
                        <div class="card-path">${{item.name}}</div>
                    </div>
                    <div class="card-hint">${{translations[currentLang].click_to_open}}</div>
                `;
                
                card.addEventListener('click', () => openFolder(item.path, item.name));
                container.appendChild(card);
            }});
            
            updateStats(items.length);
        }}
        
        // Open folder
        function openFolder(path, name) {{
            console.log('Opening folder:', path);
            
            // Copy path to clipboard
            navigator.clipboard.writeText(path).then(() => {{
                console.log('Path copied to clipboard:', path);
                
                // Show confirmation
                const t = translations[currentLang];
                alert(`${{t.open_folder}}: ${{name}}\\n\\nPath copied to clipboard:\\n${{path}}\\n\\nTrying to open folder...`);
                
                // Try to open via API
                fetch('/api/open-folder', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                    }},
                    body: JSON.stringify({{ path: path }})
                }}).catch(error => {{
                    console.log('API call failed, using fallback:', error);
                }});
            }}).catch(err => {{
                console.error('Copy failed:', err);
                const t = translations[currentLang];
                alert(`${{t.open_folder}}: ${{name}}\\n\\nPath:\\n${{path}}`);
            }});
        }}
        
        // Filter items
        function filterItems(searchTerm = '') {{
            let itemsToShow;
            
            if (activeCategory === 'all') {{
                itemsToShow = allItems;
            }} else {{
                itemsToShow = allCategories[activeCategory] || [];
            }}
            
            if (searchTerm) {{
                itemsToShow = itemsToShow.filter(item => 
                    item.name.toLowerCase().includes(searchTerm) ||
                    item.category.toLowerCase().includes(searchTerm)
                );
            }}
            
            renderItems(itemsToShow);
        }}
        
        // Update stats
        function updateStats(count) {{
            document.getElementById('showingCount').textContent = count;
        }}
        
        // Setup event listeners
        function setupEventListeners() {{
            // Search
            const searchInput = document.getElementById('searchInput');
            searchInput.addEventListener('input', function(e) {{
                const searchTerm = e.target.value.toLowerCase().trim();
                filterItems(searchTerm);
            }});
            
            // Language switching
            document.querySelectorAll('.lang-btn').forEach(btn => {{
                btn.addEventListener('click', function() {{
                    const lang = this.dataset.lang;
                    currentLang = lang;
                    
                    // Update active language button
                    document.querySelectorAll('.lang-btn').forEach(b => {{
                        b.classList.toggle('active', b.dataset.lang === lang);
                    }});
                    
                    updateLanguage(lang);
                }});
            }});
            
            // Keyboard shortcuts
            document.addEventListener('keydown', (e) => {{
                // Ctrl+F or / to focus search
                if ((e.ctrlKey && e.key === 'f') || e.key === '/') {{
                    e.preventDefault();
                    searchInput.focus();
                }}
                
                // Escape to clear search
                if (e.key === 'Escape' && document.activeElement === searchInput) {{
                    searchInput.value = '';
                    filterItems('');
                    searchInput.blur();
                }}
            }});
        }}
        
        // Update language
        function updateLanguage(lang) {{
            currentLang = lang;
            const t = translations[lang];
            
            // Update page title
            const totalItems = allItems.length;
            const totalCategories = Object.keys(allCategories).length;
            document.title = `${{t.title}} - ${{totalCategories}} ${{t.categories}}, ${{totalItems}} ${{t.items}}`;
            
            // Update search placeholder
            document.getElementById('searchInput').placeholder = t.search_placeholder;
            
            // Update stat labels
            const statLabels = document.querySelectorAll('.stat-label');
            if (statLabels.length >= 4) {{
                statLabels[0].textContent = t.total_categories;
                statLabels[1].textContent = t.total_items;
                statLabels[2].textContent = t.showing;
                statLabels[3].textContent = t.last_updated;
            }}
            
            // Update category title
            const titleElement = document.getElementById('activeCategoryTitle');
            if (activeCategory === 'all') {{
                titleElement.innerHTML = `${{t.view_all}} (<span>${{allItems.length}}</span> ${{t.items.toLowerCase()}})`;
            }} else {{
                const count = allCategories[activeCategory].length;
                titleElement.innerHTML = `<span>${{activeCategory}}</span> - ${{count}} ${{t.items.toLowerCase()}}`;
            }}
            
            // Update footer
            document.querySelector('.footer p').textContent = 
                `${{t.title}} | ${{Object.keys(allCategories).length}} ${{t.categories}} | ${{allItems.length}} ${{t.items}} | © ${{new Date().getFullYear()}}`;
            
            // Update card hints
            document.querySelectorAll('.card-hint').forEach(hint => {{
                hint.textContent = t.click_to_open;
            }});
            
            // Update category tabs (All tab)
            const allTab = document.querySelector('[data-category="all"]');
            if (allTab) {{
                allTab.innerHTML = `${{t.all}} <span class="count">${{allItems.length}}</span>`;
            }}
        }}
        
        // Initialize on load
        document.addEventListener('DOMContentLoaded', init);
    </script>
</body>
</html>''')
    
    # 将所有部分合并为完整的HTML
    html_content = ''.join(html_parts)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Generated HTML file: {output_file}")
    print(f"📊 Found {total_categories} categories with {total_items} total items")
    
    return output_file

class GalleryHTTPHandler(http.server.SimpleHTTPRequestHandler):
    """自定义HTTP处理器，支持打开文件夹API"""
    
    def do_POST(self):
        """处理POST请求"""
        if self.path == '/api/open-folder':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                path = data.get('path', '')
                success = open_folder(path)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {'success': success, 'path': path}
                self.wfile.write(json.dumps(response).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode('utf-8'))
        else:
            super().do_GET()
    
    def log_message(self, format, *args):
        """禁用日志输出"""
        pass

def start_server(port=8000, directory='.'):
    """启动本地服务器"""
    os.chdir(directory)
    
    try:
        with socketserver.TCPServer(("", port), GalleryHTTPHandler) as httpd:
            server_url = f"http://localhost:{port}/gallery.html"
            print(f"🌐 Local server started: {server_url}")
            print("📱 Press Ctrl+C to stop the server")
            
            # 延迟打开浏览器
            def open_browser():
                time.sleep(1)
                webbrowser.open(server_url)
            
            threading.Thread(target=open_browser, daemon=True).start()
            
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
    except Exception as e:
        print(f"❌ Server failed to start: {e}")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Universal Resource Gallery Generator')
    parser.add_argument('directory', nargs='?', default='.', help='Directory to scan (default: current)')
    parser.add_argument('--lang', default='en-US', choices=['zh-CN', 'ja-JP', 'ko-KR', 'en-US'],
                       help='Default language (zh-CN, ja-JP, ko-KR, en-US)')
    parser.add_argument('--serve', action='store_true', help='Start local server')
    parser.add_argument('--port', type=int, default=8000, help='Server port')
    parser.add_argument('--output', default='gallery.html', help='Output HTML filename')
    
    args = parser.parse_args()
    
    # 检查目录
    if not os.path.exists(args.directory):
        print(f"❌ Directory not found: {args.directory}")
        print(f"📁 Current directory: {os.getcwd()}")
        return
    
    # 扫描目录
    categories = scan_directory(args.directory)
    
    if not categories:
        print("❌ No categories found")
        print("💡 Make sure the directory contains subdirectories with content")
        return
    
    # 生成HTML
    html_file = generate_html(categories, output_file=args.output, lang=args.lang)
    
    # 启动服务器或直接打开
    if args.serve:
        start_server(port=args.port, directory=os.path.dirname(os.path.abspath(html_file)))
    else:
        html_path = os.path.abspath(html_file)
        try:
            webbrowser.open(f"file:///{html_path}")
            print(f"📄 Opened in browser: {html_path}")
        except:
            print(f"📄 Please open manually in browser: {html_path}")

if __name__ == "__main__":
    main()
