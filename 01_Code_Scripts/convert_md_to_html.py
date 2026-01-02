
import markdown
import os
import sys
import base64
import re
from pathlib import Path

# 设置输入输出路径
MD_FILE_PATH = r"C:\Users\weirui\Desktop\AI_Test\AI辅助白内障筛查实践报告_converted.md"
HTML_FILE_PATH = r"C:\Users\weirui\Desktop\AI_Test\AI辅助白内障筛查实践报告_最终版.html"

def image_to_base64(image_path):
    """将图片文件转换为 Base64 编码字符串"""
    try:
        if not os.path.exists(image_path):
            print(f"Warning: Image not found: {image_path}")
            return None
            
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            
        # 根据扩展名确定 MIME type
        ext = os.path.splitext(image_path)[1].lower()
        if ext in ['.jpg', '.jpeg']:
            mime_type = 'image/jpeg'
        elif ext == '.png':
            mime_type = 'image/png'
        elif ext == '.gif':
            mime_type = 'image/gif'
        elif ext == '.svg':
            mime_type = 'image/svg+xml'
        else:
            mime_type = 'image/png' # Default
            
        return f"data:{mime_type};base64,{encoded_string}"
    except Exception as e:
        print(f"Error encoding image {image_path}: {e}")
        return None

def embed_images(html_content, base_dir):
    """查找 HTML 中的 img 标签并将 src 替换为 Base64"""
    # 正则匹配 <img src="..." ...>
    # 捕获 src 的内容
    img_pattern = re.compile(r'<img[^>]+src="([^">]+)"[^>]*>')
    
    def replace_match(match):
        src_path = match.group(1)
        
        # 如果已经是 base64，直接返回
        if src_path.startswith("data:"):
            return match.group(0)
            
        # Handle file:// prefix
        if src_path.startswith("file:///"):
            src_path = src_path[8:]
        elif src_path.startswith("file://"):
            src_path = src_path[7:]
            
        # Normalize path separators
        src_path = os.path.normpath(src_path)

        # 构建绝对路径
        if os.path.isabs(src_path):
            abs_path = src_path
        else:
            abs_path = os.path.join(base_dir, src_path)
        
        # 转换
        base64_data = image_to_base64(abs_path)
        
        if base64_data:
            # 替换 src 属性
            # 为了安全，重新构建整个 img 标签有点麻烦，还是直接替换 src 字符串更简单
            return match.group(0).replace(src_path, base64_data)
        else:
            return match.group(0)
            
    return img_pattern.sub(replace_match, html_content)

def convert_md_to_html(md_path, html_path):
    print(f"Converting {md_path} to {html_path}...")
    
    try:
        with open(md_path, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        print(f"Error reading markdown file: {e}")
        return

    # Convert to HTML
    # 使用 extra 扩展以支持表格等，toc 扩展支持目录
    html_body = markdown.markdown(text, extensions=['extra', 'codehilite', 'tables', 'toc'])
    
    # 嵌入图片
    base_dir = os.path.dirname(md_path)
    print("Embedding images...")
    html_body = embed_images(html_body, base_dir)

    # HTML Template
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>AI辅助白内障筛查实践报告</title>
        <style>
            body {{
                font-family: "Microsoft YaHei", "SimSun", sans-serif;
                font-size: 11pt;
                line-height: 1.6;
                padding: 40px;
                color: #333;
                max-width: 900px;
                margin: 0 auto;
                background-color: #fff;
            }}
            
            @media print {{
                body {{
                    max-width: 100%;
                    padding: 0;
                }}
            }}
            
            h1 {{ font-size: 24pt; color: #000; text-align: center; margin-bottom: 24px; border-bottom: 2px solid #333; padding-bottom: 10px; }}
            h2 {{ font-size: 16pt; color: #2980b9; border-bottom: 1px solid #eee; padding-bottom: 8px; margin-top: 32px; }}
            h3 {{ font-size: 14pt; color: #34495e; margin-top: 24px; }}
            
            /* Code Blocks (IDE Style) */
            pre {{
                background-color: #1e1e1e; /* Dark background */
                color: #d4d4d4;
                border: 1px solid #333;
                padding: 15px;
                border-radius: 5px;
                overflow-x: auto;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 10pt;
            }}
            code {{
                font-family: 'Consolas', 'Courier New', monospace;
            }}
            
            blockquote {{
                background: #fdfdfd;
                border-left: 5px solid #3498db;
                margin: 1.5em 0;
                padding: 10px 20px;
                font-style: italic;
                color: #555;
            }}
            
            img {{
                max-width: 80%; /* 限制图片大小 */
                height: auto;
                display: block;
                margin: 15px auto;
                border: 1px solid #eee;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            
            table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 8px 12px; }}
            th {{ background-color: #f2f2f2; }}
            
            a {{ color: #0366d6; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
        </style>
    </head>
    <body>
        <div style="text-align:center; margin-bottom:40px;">
           <p style="color:#666; font-size:0.9em;">生成时间: 2026-01-02</p>
        </div>
        {html_body}
    </body>
    </html>
    """

    try:
        with open(html_path, "w", encoding='utf-8') as f:
            f.write(html_content)
        print(f"HTML successfully created at: {html_path}")
            
    except Exception as e:
        print(f"Failed to write HTML file: {e}")

if __name__ == "__main__":
    convert_md_to_html(MD_FILE_PATH, HTML_FILE_PATH)
