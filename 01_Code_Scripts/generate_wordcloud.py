import os
import jieba
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re

# 配置
BASE_DIR = r"c:\Users\weirui\Desktop\AI_Test"
OUTPUT_FILE = r"c:\Users\weirui\Desktop\AI_Test\project_wordcloud.png"
FONT_PATH = r"C:\Windows\Fonts\msyh.ttc"

EXTENSIONS = {'.py', '.js', '.html', '.css', '.md'}
EXCLUDE_DIRS = {
    'node_modules', '.git', '.gemini', '__pycache__', 'dist', 'build', 
    'venv', 'env', '.idea', '.vscode', 'assets', 'images'
}

# 扩展停用词表：去除对业务理解无用的编程关键词
STOPWORDS = {
    # Python Keywords & Common
    'import', 'from', 'in', 'as', 'if', 'else', 'elif', 'for', 'while', 'break', 'continue',
    'def', 'class', 'return', 'try', 'except', 'finally', 'with', 'pass', 'lambda', 'yield',
    'True', 'False', 'None', 'self', 'print', 'range', 'len', 'open', 'str', 'int', 'float',
    'list', 'dict', 'set', 'tuple', 'id', 'type', 'main', 'name', 'file', 'path', 'os', 'sys',
    'join', 'encoding', 'utf', 'read', 'write', 'append', 'split', 'strip', 'replace',
    
    # JS/HTML/CSS Keywords
    'var', 'let', 'const', 'function', 'return', 'if', 'else', 'for', 'while', 'switch', 'case',
    'break', 'continue', 'default', 'try', 'catch', 'finally', 'throw', 'new', 'this', 'typeof',
    'instanceof', 'void', 'delete', 'async', 'await', 'export', 'import', 'true', 'false', 'null',
    'undefined', 'NaN', 'console', 'log', 'document', 'window', 'getElementById', 'addEventListener',
    'div', 'span', 'p', 'a', 'img', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li',
    'table', 'tr', 'td', 'th', 'tbody', 'thead', 'form', 'input', 'button', 'script', 'style',
    'link', 'meta', 'head', 'body', 'html', 'title', 'class', 'id', 'src', 'href', 'style',
    'width', 'height', 'top', 'left', 'right', 'bottom', 'color', 'background', 'border',
    'margin', 'padding', 'display', 'position', 'absolute', 'relative', 'flex', 'grid',
    'px', 'em', 'rem', 'rgb', 'rgba', 'solid', 'none', 'block', 'inline', 'font', 'size',
    'text', 'align', 'center', 'justify', 'content', 'items', 'z-index', 'opacity', 'cursor',
    'pointer', 'hidden', 'visible', 'overflow', 'auto', 'radius', 'shadow', 'box', 'transition',
    'transform', 'translate', 'rotate', 'scale', 'animation', 'keyframes', 'media', 'query',
    
    # Common Generic Terms
    'test', 'data', 'file', 'path', 'dir', 'name', 'value', 'key', 'index', 'item', 'list',
    'array', 'object', 'string', 'number', 'boolean', 'json', 'xml', 'http', 'https', 'url',
    'get', 'post', 'put', 'delete', 'api', 'res', 'req', 'err', 'error', 'result', 'response',
    'request', 'config', 'option', 'setting', 'param', 'arg', 'args', 'kwargs', 'init', 'update',
    'create', 'delete', 'remove', 'add', 'check', 'verify', 'validate', 'process', 'handle',
    'click', 'change', 'submit', 'event', 'target', 'element', 'node', 'parent', 'child',
    'step', 'max', 'min', 'avg', 'sum', 'count', 'total', 'start', 'end', 'stop', 'pause',
    'play', 'show', 'hide', 'toggle', 'open', 'close', 'load', 'save', 'select', 'cancel',
    'type', 'status', 'mode', 'state', 'flag', 'user', 'system', 'app', 'project', 'version',
    'code', 'line', 'column', 'row', 'group', 'section', 'header', 'footer', 'nav', 'main',
    'sidebar', 'menu', 'button', 'icon', 'label', 'title', 'desc', 'info', 'warn', 'debug',
    'log', 'print', 'output', 'input', 'message', 'msg', 'txt', 'csv', 'xls', 'xlsx', 'doc',
    'docx', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'svg', 'bmp', 'ico', 'base64', 'binary',
    'byte', 'bit', 'kb', 'mb', 'gb', 'tb', 'time', 'date', 'year', 'month', 'day', 'hour',
    'minute', 'second', 'now', 'timestamp', 'timeout', 'interval', 'delay', 'wait', 'sleep',
    'todo', 'fix', 'bug', 'issue', 'feature', 'task', 'plan', 'review', 'comment', 'note',
    'and', 'or', 'not', 'is', 'the', 'a', 'an', 'to', 'of', 'in', 'on', 'at', 'by', 'for',
    'with', 'about', 'as', 'into', 'like', 'through', 'after', 'over', 'between', 'out',
    'against', 'during', 'without', 'before', 'under', 'around', 'among',
    'com', 'cn', 'net', 'org', 'www', 'zh', 'en'
}

def scan_files(base_dir):
    text_content = ""
    file_count = 0
    print(f"Scanning files in {base_dir}...")
    
    for root, dirs, files in os.walk(base_dir):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in EXTENSIONS:
                if '.min.' in file: continue
                file_path = os.path.join(root, file)
                if os.path.getsize(file_path) > 200 * 1024: continue # Skip > 200KB

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        text_content += f.read() + "\n"
                        file_count += 1
                except:
                    continue
    
    print(f"Scanned {file_count} files.")
    return text_content

from collections import Counter

# ... (previous config) ...

# 权重提升关键词
MEDICAL_KEYWORDS = {
    'cataract', 'normal', 'fundus', 'eye', 'medical', 'diagnosis', 'symptom', 
    'patient', 'hospital', 'sysu', 'doctor', 'disease', 'vision', 'health', 
    'retina', 'ophthalmology', 'clinical', 'detect', 'screen', 'ai', 'med'
}

TECH_KEYWORDS = {
    'chart', 'visualization', 'model', 'accuracy', 'precision', 'recall', 'f1', 
    'pytorch', 'tensor', 'algorithm', 'classification', 'heatmap', 'gradcam', 
    'conf', 'matrix', 'roc', 'auc', 'deep', 'learning', 'neural', 'network',
    'train', 'test', 'val', 'predict', 'inference', 'data', 'dataset', 'image',
    'analysis', 'performance', 'evaluate', 'metric', 'statistics', 'dashboard'
}

# 扩展停用词表
STOPWORDS.add('weirui') # 用户名
STOPWORDS.add('users')
STOPWORDS.add('desktop')

def generate_cloud(text):
    print("Processing text...")
    
    # 清理非中英文字符（保留数字供型号使用）
    text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9]', ' ', text)
    
    words = jieba.cut(text)
    filtered_words = []
    
    # 初步过滤
    for word in words:
        word = word.strip()
        if len(word) > 1 and word.lower() not in STOPWORDS and not word.isdigit():
            # 统一转小写进行统计（或者保持原样，视需求而定。通常保持原样对专有名词更好，但这里为了匹配方便，统计时可以归一化）
            #这里保持原样，但在判断权重时转小写
            filtered_words.append(word)
            
    # 计算词频
    frequency = Counter(filtered_words)
    
    # 应用权重调整
    print("Applying custom weights...")
    for word, count in frequency.items():
        w_lower = word.lower()
        if w_lower in MEDICAL_KEYWORDS:
            frequency[word] = count * 3.0  # 医学词汇权重调低至 x3 (与技术词汇持平)
        elif w_lower in TECH_KEYWORDS:
            frequency[word] = count * 3.0  # 技术词汇权重 x3
            
    print(f"Generating WordCloud (Unique words: {len(frequency)})...")
    
    # 优化配置
    wc = WordCloud(
        font_path=FONT_PATH,
        width=2000,
        height=1200,
        background_color='white',
        mode='RGB',
        max_words=150,
        mask=None,
        prefer_horizontal=0.9,
        relative_scaling=0.5,
        colormap='tab10',
        stopwords=STOPWORDS, # 虽然用了 frequency，stopwords 参数主要用于 generate(text)，但保留也无妨
        regexp=r"\w[\w']+"
    )
    
    # 使用 generate_from_frequencies 代替 generate
    wc.generate_from_frequencies(frequency)
    
    print(f"Saving to {OUTPUT_FILE}...")
    wc.to_file(OUTPUT_FILE)
    print("Done!")

if __name__ == "__main__":
    content = scan_files(BASE_DIR)
    if content:
        generate_cloud(content)
    else:
        print("No content found.")
