from flask import Flask, send_file, jsonify, request
from flask_cors import CORS
import os
import sys
import threading
import webbrowser
import time
from datetime import datetime

app = Flask(__name__)
CORS(app)  # 启用CORS支持

# 获取脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VIDEO_DIR = os.path.join(SCRIPT_DIR, 'video')

# 确保video目录存在
if not os.path.exists(VIDEO_DIR):
    os.makedirs(VIDEO_DIR)

# 多语言文本定义
# 多语言文本定义
LANGUAGES = {
    'en': {
        'title': '🎬 VRChat Local Video Server',
        'server_status': 'Server Status',
        'running': '● Running',
        'last_updated': 'Last Updated',
        'videos_found': 'video files found',
        'video_name': 'Video Name',
        'file_size': 'File Size',
        'copy_url': 'Copy URL',
        'copied': 'Copied',
        'instructions': 'Usage Instructions',
        'instruction1': '1. Click the URL or "Copy" button to copy the video link',
        'instruction2': '2. Paste the URL in VRChat video player',
        'instruction3': '3. Only you can see these videos (local server)',
        'instruction4': '4. Can only be used in non-public worlds',
        'no_videos': 'No video files found',
        'video_dir': 'Video Directory',
        'supported_formats': 'Supported Formats',
        'server_address': 'Server Address',
        'click_to_copy': 'Click to copy',
        'language': 'Language',
        'refresh': 'Refresh'
    },
    'zh': {
        'title': '🎬 VRChat 本地视频服务器',
        'server_status': '服务器状态',
        'running': '● 运行中',
        'last_updated': '最后更新',
        'videos_found': '个视频文件',
        'video_name': '视频名称',
        'file_size': '文件大小',
        'copy_url': '复制链接',
        'copied': '已复制',
        'instructions': '使用说明',
        'instruction1': '1. 点击URL或"复制"按钮复制视频链接',
        'instruction2': '2. 在VRChat视频播放器中粘贴该URL',
        'instruction3': '3. 只有您自己能看到这些视频（本地服务器）',
        'instruction4': '4. 只可以在非公开世界使用',
        'no_videos': '未找到视频文件',
        'video_dir': '视频目录',
        'supported_formats': '支持格式',
        'server_address': '服务器地址',
        'click_to_copy': '点击复制',
        'language': '语言',
        'refresh': '刷新'
    },
    'zh-tw': {
        'title': '🎬 VRChat 本地影片伺服器',
        'server_status': '伺服器狀態',
        'running': '● 運行中',
        'last_updated': '最後更新',
        'videos_found': '個影片檔案',
        'video_name': '影片名稱',
        'file_size': '檔案大小',
        'copy_url': '複製連結',
        'copied': '已複製',
        'instructions': '使用說明',
        'instruction1': '1. 點擊URL或"複製"按鈕複製影片連結',
        'instruction2': '2. 在VRChat影片播放器中貼上該URL',
        'instruction3': '3. 只有您自己能看到這些影片（本地伺服器）',
        'instruction4': '4. 只可以在非公開世界使用',
        'no_videos': '未找到影片檔案',
        'video_dir': '影片目錄',
        'supported_formats': '支援格式',
        'server_address': '伺服器地址',
        'click_to_copy': '點擊複製',
        'language': '語言',
        'refresh': '重新整理'
    },
    'ja': {
        'title': '🎬 VRChat ローカルビデオサーバー',
        'server_status': 'サーバー状態',
        'running': '● 実行中',
        'last_updated': '最終更新',
        'videos_found': '個の動画ファイルが見つかりました',
        'video_name': '動画名',
        'file_size': 'ファイルサイズ',
        'copy_url': 'URLをコピー',
        'copied': 'コピーしました',
        'instructions': '使用方法',
        'instruction1': '1. URLまたは「コピー」ボタンをクリックして動画リンクをコピー',
        'instruction2': '2. VRChatのビデオプレイヤーにURLを貼り付け',
        'instruction3': '3. これらの動画は自分だけが見ることができます（ローカルサーバー）',
        'instruction4': '4. 非公開ワールドでのみ使用できます',
        'no_videos': '動画ファイルが見つかりません',
        'video_dir': '動画ディレクトリ',
        'supported_formats': '対応形式',
        'server_address': 'サーバーアドレス',
        'click_to_copy': 'クリックでコピー',
        'language': '言語',
        'refresh': '更新'
    },
    'ko': {
        'title': '🎬 VRChat 로컬 비디오 서버',
        'server_status': '서버 상태',
        'running': '● 실행 중',
        'last_updated': '마지막 업데이트',
        'videos_found': '개의 비디오 파일을 찾았습니다',
        'video_name': '비디오 이름',
        'file_size': '파일 크기',
        'copy_url': 'URL 복사',
        'copied': '복사되었습니다',
        'instructions': '사용 설명',
        'instruction1': '1. URL 또는 "복사" 버튼을 클릭하여 비디오 링크 복사',
        'instruction2': '2. VRChat 비디오 플레이어에 URL 붙여넣기',
        'instruction3': '3. 이러한 비디오는 본인만 볼 수 있습니다 (로컬 서버)',
        'instruction4': '4. 비공개 월드에서만 사용할 수 있습니다',
        'no_videos': '비디오 파일을 찾을 수 없습니다',
        'video_dir': '비디오 디렉토리',
        'supported_formats': '지원 형식',
        'server_address': '서버 주소',
        'click_to_copy': '클릭하여 복사',
        'language': '언어',
        'refresh': '새로고침'
    }
}


def get_video_files():
    """获取video目录下的所有视频文件"""
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.wmv', '.flv']
    video_files = []
    
    if os.path.exists(VIDEO_DIR):
        for file in os.listdir(VIDEO_DIR):
            file_path = os.path.join(VIDEO_DIR, file)
            if os.path.isfile(file_path) and any(file.lower().endswith(ext) for ext in video_extensions):
                # 获取文件大小
                size = os.path.getsize(file_path)
                size_mb = round(size / (1024 * 1024), 2)
                video_files.append({
                    'name': file,
                    'size_mb': size_mb,
                    'url': f'http://localhost:14514/video/{file}'
                })
    
    return sorted(video_files, key=lambda x: x['name'])

def print_video_list():
    """在控制台打印视频列表和URL"""
    video_files = get_video_files()
    
    print("\n" + "="*70)
    print("视频文件列表及访问URL")
    print("="*70)
    
    if not video_files:
        print("❌ 未找到视频文件")
        print(f"请将视频文件放入: {VIDEO_DIR}")
        return
    
    for i, video in enumerate(video_files, 1):
        print(f"{i:2d}. {video['name']} ({video['size_mb']} MB)")
        print(f"    🔗 {video['url']}")
    
    print("="*70)
    print("💡 提示: 在VRChat视频播放器中输入上述URL即可播放")
    print("="*70)

@app.route('/')
def index():
    """显示可用的视频文件列表"""
    # 获取语言参数，默认为中文
    lang = request.args.get('lang', 'zh')
    if lang not in LANGUAGES:
        lang = 'zh'
    
    video_files = get_video_files()
    strings = LANGUAGES[lang]
    
    if not video_files:
        return f"""
        <html>
            <head>
                <title>{strings['title']}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
                    .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                    .warning {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                    code {{ background: #f8f9fa; padding: 10px; border-radius: 3px; display: block; margin: 10px 0; }}
                    .lang-selector {{ text-align: right; margin-bottom: 20px; }}
                    .lang-btn {{ 
                        background: #6c757d; 
                        color: white; 
                        border: none; 
                        padding: 5px 10px; 
                        border-radius: 3px; 
                        margin: 0 2px; 
                        cursor: pointer;
                    }}
                    .lang-btn.active {{ background: #007bff; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="lang-selector">
                        {generate_language_selector(lang)}
                    </div>
                    <h1>{strings['title']}</h1>
                    <div class="warning">
                        <strong>⚠️ {strings['no_videos']}</strong>
                        <p>{strings['video_dir']}:</p>
                        <code>{VIDEO_DIR}</code>
                    </div>
                    <p><strong>{strings['supported_formats']}:</strong> MP4, AVI, MOV, MKV, WebM, WMV, FLV</p>
                    <p><strong>{strings['server_status']}:</strong> <span style="color: green;">{strings['running']}</span></p>
                    <p><em>{strings['last_updated']}: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</em></p>
                </div>
            </body>
        </html>
        """
    
    html = f"""
    <html>
        <head>
            <title>{strings['title']}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
                .container {{ max-width: 1000px; margin: 0 auto; }}
                .header {{ background: white; padding: 20px; border-radius: 10px 10px 0 0; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
                .video-list {{ background: white; padding: 20px; border-radius: 0 0 10px 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin-top: 10px; }}
                .video-item {{ 
                    margin: 15px 0; 
                    padding: 15px; 
                    background: #f8f9fa; 
                    border-radius: 5px; 
                    border-left: 4px solid #007bff;
                    transition: all 0.3s;
                }}
                .video-item:hover {{ background: #e9ecef; }}
                .video-name {{ font-weight: bold; font-size: 16px; margin-bottom: 5px; }}
                .video-url {{ 
                    background: white; 
                    padding: 8px 12px; 
                    border-radius: 3px; 
                    font-family: 'Courier New', monospace; 
                    border: 1px solid #dee2e6;
                    user-select: all;
                    cursor: pointer;
                }}
                .video-meta {{ color: #6c757d; font-size: 14px; margin-top: 5px; }}
                .copy-btn {{ 
                    background: #007bff; 
                    color: white; 
                    border: none; 
                    padding: 5px 10px; 
                    border-radius: 3px; 
                    cursor: pointer;
                    margin-left: 10px;
                }}
                .status {{ color: green; font-weight: bold; }}
                .lang-selector {{ text-align: right; margin-bottom: 20px; }}
                .lang-btn {{ 
                    background: #6c757d; 
                    color: white; 
                    border: none; 
                    padding: 5px 10px; 
                    border-radius: 3px; 
                    margin: 0 2px; 
                    cursor: pointer;
                }}
                .lang-btn.active {{ background: #007bff; }}
                .refresh-btn {{
                    background: #28a745;
                    color: white;
                    border: none;
                    padding: 5px 10px;
                    border-radius: 3px;
                    cursor: pointer;
                    margin-left: 10px;
                }}
            </style>
            <script>
                function copyToClipboard(text) {{
                    navigator.clipboard.writeText(text).then(function() {{
                        alert('{strings['copied']}: ' + text);
                    }}, function(err) {{
                        console.error('{strings['copy_url']} failed: ', err);
                    }});
                }}
                
                function changeLanguage(lang) {{
                    window.location.href = '/?lang=' + lang;
                }}
                
                function refreshPage() {{
                    window.location.reload();
                }}
            </script>
        </head>
        <body>
            <div class="container">
                <div class="lang-selector">
                    {generate_language_selector(lang)}
                    <button class="refresh-btn" onclick="refreshPage()">{strings['refresh']}</button>
                </div>
                
                <div class="header">
                    <h1>{strings['title']}</h1>
                    <p><strong>{len(video_files)}</strong> {strings['videos_found']}</p>
                    <p><strong>{strings['server_status']}:</strong> <span class="status">{strings['running']}</span></p>
                    <p><em>{strings['last_updated']}: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</em></p>
                </div>
                
                <div class="video-list">
    """
    
    for i, video in enumerate(video_files, 1):
        html += f"""
                    <div class="video-item">
                        <div class="video-name">{i}. {video['name']}</div>
                        <div>
                            <span class="video-url" onclick="copyToClipboard('{video['url']}')" title="{strings['click_to_copy']}">{video['url']}</span>
                            <button class="copy-btn" onclick="copyToClipboard('{video['url']}')">{strings['copy_url']}</button>
                        </div>
                        <div class="video-meta">{strings['file_size']}: {video['size_mb']} MB</div>
                    </div>
        """
    
    html += f"""
                </div>
                <div style="margin-top: 20px; padding: 15px; background: #d4edda; border-radius: 5px;">
                    <strong>💡 {strings['instructions']}:</strong>
                    <p>{strings['instruction1']}</p>
                    <p>{strings['instruction2']}</p>
                    <p>{strings['instruction3']}</p>
                    <p>{strings['instruction4']}</p>
                </div>
            </div>
        </body>
    </html>
    """
    
    return html

def generate_language_selector(current_lang):
    """生成语言选择器HTML"""
    lang_names = {
        'en': 'English',
        'zh': '简体中文',
        'zh-tw': '繁體中文',
        'ja': '日本語',
        'ko': '한국어'
    }
    
    html = f'<span style="margin-right: 10px;">{LANGUAGES[current_lang]["language"]}:</span>'
    for lang_code, lang_name in lang_names.items():
        active_class = 'active' if lang_code == current_lang else ''
        html += f'<button class="lang-btn {active_class}" onclick="changeLanguage(\'{lang_code}\')">{lang_name}</button>'
    
    return html

@app.route('/video/<filename>')
def serve_video(filename):
    """提供视频文件流"""
    video_path = os.path.join(VIDEO_DIR, filename)
    
    # 安全检查：确保文件在video目录内
    if not os.path.abspath(video_path).startswith(os.path.abspath(VIDEO_DIR)):
        return "禁止访问", 403
    
    if not os.path.exists(video_path):
        return "视频文件不存在", 404
    
    # 设置适当的MIME类型
    mime_types = {
        '.mp4': 'video/mp4',
        '.avi': 'video/x-msvideo',
        '.mov': 'video/quicktime',
        '.mkv': 'video/x-matroska',
        '.webm': 'video/webm',
        '.wmv': 'video/x-ms-wmv',
        '.flv': 'video/x-flv'
    }
    
    ext = os.path.splitext(filename)[1].lower()
    mime_type = mime_types.get(ext, 'video/mp4')
    
    return send_file(video_path, mimetype=mime_type)

@app.route('/api/videos')
def list_videos_api():
    """API接口：返回视频文件列表"""
    return jsonify(get_video_files())

def open_browser():
    """在默认浏览器中打开服务器页面"""
    time.sleep(2)  # 等待服务器启动
    webbrowser.open('http://localhost:14514')

if __name__ == '__main__':
    print("=" * 70)
    print("🎬 VRChat 本地视频服务器启动中...")
    print("=" * 70)
    print(f"📁 视频文件目录: {VIDEO_DIR}")
    print("📹 支持格式: MP4, AVI, MOV, MKV, WebM, WMV, FLV")
    print("🌐 服务器地址: http://localhost:14514")
    print("🗣️  支持语言: 简体中文, 繁體中文, English, 日本語, 한국어")
    print("=" * 70)
    
    # 打印视频列表
    print_video_list()
    
    # 在浏览器中打开页面
    threading.Thread(target=open_browser, daemon=True).start()
    
    # 启动Flask服务器
    try:
        app.run(host='0.0.0.0', port=14514, debug=False)
    except KeyboardInterrupt:
        print("\n\n服务器已停止")
