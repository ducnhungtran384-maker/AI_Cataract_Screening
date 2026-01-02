
from docx2pdf import convert
import os
import sys
import pythoncom

def convert_to_pdf(docx_path, pdf_path):
    print(f"Converting {docx_path} to {pdf_path}...")
    abs_docx = os.path.abspath(docx_path)
    abs_pdf = os.path.abspath(pdf_path)
    
    try:
        # Initialize COM for Windows
        pythoncom.CoInitialize()
        convert(abs_docx, abs_pdf)
        print(f"Success! PDF generated at: {abs_pdf}")
    except Exception as e:
        print(f"Error during conversion: {e}")
        print("Ensure Microsoft Word is installed and not blocked.")

if __name__ == "__main__":
    docx_file = r"C:\Users\weirui\Desktop\AI_Test\AI辅助白内障筛查实践报告_最终排版.docx"
    pdf_file = r"C:\Users\weirui\Desktop\AI_Test\AI辅助白内障筛查实践报告_最终版.pdf"
    
    convert_to_pdf(docx_file, pdf_file)
