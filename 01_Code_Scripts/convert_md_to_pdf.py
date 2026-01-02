
import markdown
from xhtml2pdf import pisa
import os
import sys

def convert_md_to_pdf(md_file_path, pdf_file_path):
    print(f"Converting {md_file_path} to {pdf_file_path}...")
    
    # 1. Read Markdown
    try:
        with open(md_file_path, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        print(f"Error reading markdown file: {e}")
        return

    # Pre-process Markdown to clean image paths (strip file:// and handled absolute paths)
    import re
    # Pattern to match ![alt](url)
    def clean_image_path(match):
        alt = match.group(1)
        url = match.group(2)
        if url.startswith('file:///'):
            url = url[8:]
        elif url.startswith('file://'):
            url = url[7:]
        return f"![{alt}]({url})"

    text = re.sub(r'!\[(.*?)\]\((.*?)\)', clean_image_path, text)

    # 2. Convert to HTML
    # Using extra extensions for better table and code block support
    html_body = markdown.markdown(text, extensions=['extra', 'codehilite', 'tables', 'toc'])

    # 3. HTML Template with CSS for Chinese Support (SimSun)
    # Use ABSOLUTE local path since we copied it
    font_path = os.path.abspath("simsun.ttc")
    if not os.path.exists(font_path):
        # Fallback to system path if local missing (shouldn't happen)
        font_path = r"C:\Windows\Fonts\simsun.ttc"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            @font-face {{
                font-family: 'ChineseFont';
                src: url('{font_path}');
            }}
            
            body {{
                font-family: 'ChineseFont', sans-serif;
                font-size: 10.5pt; /* More standard document font size */
                line-height: 1.6;
                padding: 40px;
                color: #333;
            }}
            
            h1 {{ font-size: 24pt; color: #000; text-align: center; margin-bottom: 24px; }}
            h2 {{ font-size: 16pt; color: #2c3e50; border-bottom: 1px solid #eee; padding-bottom: 8px; margin-top: 24px; }}
            h3 {{ font-size: 14pt; color: #34495e; margin-top: 20px; }}
            h4 {{ font-size: 12pt; font-weight: bold; margin-top: 16px; }}
            
            p {{ margin-bottom: 12px; text-align: justify; }}
            
            /* Code Blocks */
            pre {{
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                padding: 12px;
                border-radius: 4px;
                white-space: pre-wrap;
                font-family: 'Courier New', monospace;
                font-size: 9pt;
            }}
            
            /* Quotes/Captions */
            blockquote {{
                background: #f9f9f9;
                border-left: 10px solid #ccc;
                margin: 1.5em 10px;
                padding: 0.5em 10px;
                font-style: italic;
                color: #555;
            }}
            
            /* Tables */
            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 20px 0;
            }}
            th, td {{
                border: 1px solid #dfe2e5;
                padding: 8px 12px;
                text-align: left;
            }}
            th {{
                background-color: #f2f2f2;
                font-weight: bold;
            }}
            
            /* TOC Links */
            a {{ color: #0366d6; text-decoration: none; }}
        </style>
    </head>
    <body>
        {html_body}
    </body>
    </html>
    """

    # 4. Generate PDF
    try:
        with open(pdf_file_path, "wb") as result_file:
            pisa_status = pisa.CreatePDF(
                src=html_content,
                dest=result_file,
                encoding='utf-8'
            )
            
        if pisa_status.err:
            print(f"Error during PDF generation: {pisa_status.err}")
        else:
            print(f"PDF successfully created at: {pdf_file_path}")
            
    except Exception as e:
        print(f"Failed to write PDF file: {e}")

if __name__ == "__main__":
    md_path = r"C:\Users\weirui\Desktop\AI_Test\AI辅助白内障筛查实践报告_converted.md"
    pdf_path = r"C:\Users\weirui\Desktop\AI_Test\AI辅助白内障筛查实践报告_最终版.pdf"
    
    if len(sys.argv) > 1:
        md_path = sys.argv[1]
    if len(sys.argv) > 2:
        pdf_path = sys.argv[2]
        
    convert_md_to_pdf(md_path, pdf_path)
