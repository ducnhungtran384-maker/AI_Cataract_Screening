
import docx
from docx.document import Document as _Document
from docx.oxml.text.paragraph import CT_P
from docx.oxml.table import CT_Tbl
from docx.table import _Cell, Table
from docx.text.paragraph import Paragraph
import os

def iter_block_items(parent):
    """
    Yield each paragraph and table child within *parent*, in document order.
    Each returned value is an instance of either Table or Paragraph.
    """
    if isinstance(parent, _Document):
        parent_elm = parent.element.body
    elif isinstance(parent, _Cell):
        parent_elm = parent._tc
    else:
        raise ValueError("something's not right")

    for child in parent_elm.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, parent)
        elif isinstance(child, CT_Tbl):
            yield Table(child, parent)

def convert_docx_to_md(docx_path, md_path):
    document = docx.Document(docx_path)
    md_content = []

    for block in iter_block_items(document):
        if isinstance(block, Paragraph):
            text = block.text.strip()
            if not text:
                continue
            
            style_name = block.style.name
            if 'Heading 1' in style_name:
                md_content.append(f"# {text}")
            elif 'Heading 2' in style_name:
                md_content.append(f"## {text}")
            elif 'Heading 3' in style_name:
                md_content.append(f"### {text}")
            elif 'Heading 4' in style_name:
                md_content.append(f"#### {text}")
            elif 'List Bullet' in style_name:
                md_content.append(f"- {text}")
            elif 'List Number' in style_name:
                md_content.append(f"1. {text}")
            elif 'Title' in style_name:
                md_content.append(f"# {text}")
            elif 'Subtitle' in style_name:
                md_content.append(f"### {text}")
            else:
                md_content.append(text)
            
            md_content.append("") # Empty line after paragraph

        elif isinstance(block, Table):
            # Simple markdown table conversion
            rows = block.rows
            if not rows:
                continue
                
            # Header
            header_cells = rows[0].cells
            header_row = "| " + " | ".join(cell.text.strip().replace('\n', ' ') for cell in header_cells) + " |"
            separator_row = "| " + " | ".join(["---"] * len(header_cells)) + " |"
            
            md_content.append(header_row)
            md_content.append(separator_row)
            
            # Body
            for row in rows[1:]:
                row_cells = row.cells
                row_text = "| " + " | ".join(cell.text.strip().replace('\n', ' ') for cell in row_cells) + " |"
                md_content.append(row_text)
            
            md_content.append("") # Empty line after table

    with open(md_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(md_content))
    
    print(f"Successfully converted {docx_path} to {md_path}")

if __name__ == "__main__":
    input_docx = r"C:\Users\weirui\Desktop\AI_Test\AI辅助白内障筛查实践报告.docx"
    output_md = r"C:\Users\weirui\Desktop\AI_Test\AI辅助白内障筛查实践报告_converted.md"
    
    try:
        convert_docx_to_md(input_docx, output_md)
    except Exception as e:
        print(f"Error during conversion: {e}")
