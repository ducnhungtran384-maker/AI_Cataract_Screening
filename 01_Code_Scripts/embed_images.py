import base64
import os
import re

# File paths
html_path = r'c:\Users\weirui\Desktop\AI_Test\visualization\index.html'
img1_path = r'c:\Users\weirui\Desktop\AI_Test\23626195457.jpg'
img2_path = r'c:\Users\weirui\Desktop\AI_Test\logo-introduction.png'

def get_base64_src(path, mime_type):
    with open(path, 'rb') as f:
        data = base64.b64encode(f.read()).decode('utf-8')
    return f"data:{mime_type};base64,{data}"

try:
    # Read HTML
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Get Base64 strings
    sysu_b64 = get_base64_src(img1_path, 'image/jpeg')
    med_b64 = get_base64_src(img2_path, 'image/png')

    # Replace src attributes
    # Patterns to match the specific img tags based on the file content seen previously
    # <img src="../23626195457.jpg" alt="SYSU校徽" style="...">
    
    html_content = html_content.replace('../23626195457.jpg', sysu_b64)
    html_content = html_content.replace('../logo-introduction.png', med_b64)

    # Write back
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("Successfully embedded images into index.html")

except Exception as e:
    print(f"Error: {e}")
