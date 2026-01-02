"""
离线HTML生成器 - SYSU白内障AI筛查系统
自动生成完全自包含的离线版index_offline.html
"""
import os
import base64
import urllib.request
from pathlib import Path

# 配置
BASE_DIR = Path(__file__).parent
VISUALIZATION_DIR = BASE_DIR / 'visualization'
OUTPUT_FILE = VISUALIZATION_DIR / 'index_offline.html'
INPUT_FILE = VISUALIZATION_DIR / 'index.html'

# CDN资源列表
CDN_RESOURCES = {
    'echarts': 'https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js',
    'echarts-gl': 'https://cdn.jsdelivr.net/npm/echarts-gl@2.0.9/dist/echarts-gl.min.js'
}

# Font Awesome - 需要单独下载字体文件
FA_CSS_URL = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css'
FA_FONT_URLS = [
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/webfonts/fa-solid-900.woff2',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/webfonts/fa-regular-400.woff2',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/webfonts/fa-brands-400.woff2'
]

# 本地资源
LOCAL_RESOURCES = {
    'css/style.css': VISUALIZATION_DIR / 'css' / 'style.css',
    'js/data.js': VISUALIZATION_DIR / 'js' / 'data.js',
    'js/error_data.js': VISUALIZATION_DIR / 'js' / 'error_data.js',
    'js/charts.js': VISUALIZATION_DIR / 'js' / 'charts.js'
}

# 图片资源
IMAGE_DIR = VISUALIZATION_DIR / 'error_images'
BADGE_DIR = BASE_DIR

def download_cdn(url):
    """下载CDN资源"""
    print(f"下载: {url}")
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            content_type = response.headers.get('Content-Type', '')
            content = response.read()
            # 如果是文本内容，解码为字符串
            if 'text' in content_type or 'css' in content_type or 'javascript' in content_type:
                return content.decode('utf-8')
            else:
                # 二进制内容直接返回
                return content
    except Exception as e:
        print(f"下载失败: {e}")
        return None

def process_font_awesome_css(css_content):
    """处理Font Awesome CSS，将字体文件链接替换为Base64"""
    import re
    
    # 查找CSS中的字体文件URL
    font_urls = re.findall(r'url\((https://[^)]+\.woff2[^)]*)\)', css_content)
    
    if not font_urls:
        print("  未找到字体文件链接")
        return css_content
    
    print(f"  发现 {len(font_urls)} 个字体文件链接")
    
    for font_url in font_urls:
        # 清理URL（移除引号）
        clean_url = font_url.strip('"').strip("'")
        print(f"  下载字体: {clean_url}")
        
        try:
            font_data = download_cdn(clean_url)
            if font_data and isinstance(font_data, bytes):
                # 转换为Base64
                font_b64 = base64.b64encode(font_data).decode('utf-8')
                data_uri = f'data:font/woff2;base64,{font_b64}'
                
                # 替换URL
                css_content = css_content.replace(font_url, data_uri)
                print(f"    ✅ 已转换 ({len(font_b64)} bytes)")
        except Exception as e:
            print(f"    ❌ 转换失败: {e}")
    
    return css_content

def read_local_file(path):
    """读取本地文件"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"读取失败 {path}: {e}")
        return None

def image_to_base64(image_path):
    """图片转Base64"""
    try:
        with open(image_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    except Exception as e:
        print(f"转换失败 {image_path}: {e}")
        return None

def generate_offline_html():
    """生成离线HTML"""
    print("=" * 50)
    print("开始生成离线版index_offline.html")
    print("=" * 50)
    
    # 1. 读取原始HTML
    html_content = read_local_file(INPUT_FILE)
    if not html_content:
        print("❌ 无法读取index.html!")
        return False
    
    # 2. 下载CDN资源
    print("\n📥 下载CDN资源...")
    cdn_contents = {}
    for name, url in CDN_RESOURCES.items():
        content = download_cdn(url)
        if content:
            cdn_contents[name] = content
            if isinstance(content, str):
                print(f"  ✅ {name}: {len(content)} bytes")
            else:
                print(f"  ✅ {name}: {len(content)} bytes (binary)")
        else:
            print(f"  ❌ {name} 下载失败")
            return False
    
    # 2.5 处理Font Awesome
    print("\n🎨 下载Font Awesome字体...")
    fa_css = download_cdn(FA_CSS_URL)
    if not fa_css:
        print("  ❌ Font Awesome CSS下载失败")
        return False
    print(f"  ✅ CSS: {len(fa_css)} bytes")
    
    # 下载字体文件并转为Base64
    font_replacements = {}
    for font_url in FA_FONT_URLS:
        font_name = font_url.split('/')[-1]
        print(f"  下载: {font_name}")
        font_data = download_cdn(font_url)
        if font_data and isinstance(font_data, bytes):
            font_b64 = base64.b64encode(font_data).decode('utf-8')
            data_uri = f'data:font/woff2;base64,{font_b64}'
            # 记录需要替换的URL模式
            font_replacements[f'../webfonts/{font_name}'] = data_uri
            print(f"    ✅ 已转换 ({len(font_b64)//1024} KB)")
    
    # 替换CSS中的字体URL
    for old_url, new_uri in font_replacements.items():
        fa_css = fa_css.replace(old_url, new_uri)
    
    cdn_contents['font-awesome'] = fa_css
    print(f"  ✅ Font Awesome处理完成")
    
    # 3. 读取本地资源
    print("\n📄 读取本地资源...")
    local_contents = {}
    for name, path in LOCAL_RESOURCES.items():
        content = read_local_file(path)
        if content:
            local_contents[name] = content
            print(f"  ✅ {name}: {len(content)} bytes")
        else:
            print(f"  ❌ {name} 读取失败")
            return False
    
    # 4. 转换图片
    print("\n🖼️  转换图片为Base64...")
    image_b64 = {}
    
    # 错误分析图片
    if IMAGE_DIR.exists():
        # 支持多种格式 (jpg, jpeg, png)
        for img_ext in ['*.jpg', '*.jpeg', '*.png']:
            for img_file in IMAGE_DIR.glob(img_ext):
                ext = img_file.suffix.lower().lstrip('.')
                mime_type = 'jpeg' if ext in ['jpg', 'jpeg'] else ext
                b64 = image_to_base64(img_file)
                if b64:
                    image_b64[f'error_images/{img_file.name}'] = f'data:image/{mime_type};base64,{b64}'
                    print(f"  ✅ {img_file.name} ({mime_type})")
    
    # 校徽
    for badge in ['23626195457.jpg', 'logo-introduction.png']:
        badge_path = BADGE_DIR / badge
        if badge_path.exists():
            ext = badge_path.suffix.lower().lstrip('.')
            mime_type = 'jpeg' if ext in ['jpg', 'jpeg'] else ext
            b64 = image_to_base64(badge_path)
            if b64:
                image_b64[f'../{badge}'] = f'data:image/{mime_type};base64,{b64}'
                print(f"  ✅ {badge} ({mime_type})")
    
    # 5. 替换HTML中的资源引用
    print("\n🔄 替换资源引用...")
    
    # 5. 替换资源引用 (不仅仅替换 src，也要替换 JS 中的路径)
    print("\n🔄 正在进行深度资源替换 (含动态 JS 图片)...")
    
    # 5.1 替换 CDN 链接为内嵌 script/style
    html_content = html_content.replace(
        '<script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>',
        f'<script>{cdn_contents["echarts"]}</script>'
    )
    html_content = html_content.replace(
        '<script src="https://cdn.jsdelivr.net/npm/echarts-gl@2.0.9/dist/echarts-gl.min.js"></script>',
        f'<script>{cdn_contents["echarts-gl"]}</script>'
    )
    html_content = html_content.replace(
        '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">',
        f'<style>{cdn_contents["font-awesome"]}</style>'
    )
    
    # 5.2 替换本地 CSS/JS (先替换 JS，因为 JS 里包含图片路径)
    html_content = html_content.replace(
        '<link rel="stylesheet" href="css/style.css">',
        f'<style>{local_contents["css/style.css"]}</style>'
    )
    html_content = html_content.replace(
        '<script src="js/data.js"></script>',
        f'<script>{local_contents["js/data.js"]}</script>'
    )
    html_content = html_content.replace(
        '<script src="js/error_data.js"></script>',
        f'<script>{local_contents["js/error_data.js"]}</script>'
    )
    html_content = html_content.replace(
        '<script src="js/charts.js"></script>',
        f'<script>{local_contents["js/charts.js"]}</script>'
    )
    
    # 5.3 核心修复：遍历所有转换好的图片，在整个 HTML (含内嵌 JS) 中进行全量替换
    # 这样可以解决 JS 动态加载图片无法显示的问题
    replaced_count = 0
    for img_path, b64_data in image_b64.items():
        # 定义可能的匹配模式 (针对 HTML src, CSS url, 以及 JS 字符串)
        patterns = [
            f'src="{img_path}"',
            f"src='{img_path}'",
            f'"{img_path}"',
            f"'{img_path}'",
            f'url({img_path})',
            f'url("{img_path}")',
            f"url('{img_path}')"
        ]
        
        found_in_img = False
        for p in patterns:
            if p in html_content:
                # 确定替换后的形式
                if 'src=' in p:
                    new_p = p.replace(img_path, b64_data)
                elif 'url(' in p:
                    new_p = p.replace(img_path, b64_data)
                else:
                    new_p = p.replace(img_path, b64_data)
                    
                html_content = html_content.replace(p, new_p)
                found_in_img = True
        
        if found_in_img:
            replaced_count += 1
            
    print(f"  ✅ 已深度替换 {replaced_count} 类图片的引用路径")
    
    # 6. 保存离线版
    print(f"\n💾 保存到: {OUTPUT_FILE}")
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(html_content)
        file_size = OUTPUT_FILE.stat().st_size / (1024 * 1024)
        print(f"✅ 生成成功! 文件大小: {file_size:.2f} MB")
        return True
    except Exception as e:
        print(f"❌ 保存失败: {e}")
        return False

if __name__ == '__main__':
    success = generate_offline_html()
    if success:
        print("\n" + "=" * 50)
        print("🎉 离线版生成完成!")
        print(f"📂 位置: {OUTPUT_FILE}")
        print("=" * 50)
    else:
        print("\n❌ 生成失败，请检查错误信息")
