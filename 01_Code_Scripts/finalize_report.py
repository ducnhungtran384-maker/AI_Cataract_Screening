
import os
import win32com.client
import time

def finalize_report(docx_path, pdf_path):
    print("Launching Word/WPS for final manual-simulation adjustments...")
    try:
        # Try capturing existing instance or create new
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = True
        word.DisplayAlerts = 0
    except Exception as e:
        print(f"Failed to launch Word: {e}")
        return

    abs_docx = os.path.abspath(docx_path)
    abs_pdf = os.path.abspath(pdf_path)
    
    try:
        print(f"Opening {abs_docx}...")
        doc = word.Documents.Open(abs_docx)
        time.sleep(1) # Let it load
        
        # --- NUCLEAR OPTION: SELECT ALL AND FORCE FONT ---
        print("Selecting ALL content and forcing '宋体' & 'Times New Roman'...")
        
        # 1. Iterate paragraphs to set font (Skipping Code Blocks!)
        # Code blocks have shading. We identify them by Shading.Texture != 0 (wdTextureNone)
        # or checking style name if we set it. But checking shading is robust.
        
        # Optimize: Selecting everything is fast. Iterating 10k lines is slow.
        # Strategy: Select All -> Set Font -> THEN find code blocks and Restore Consolas?
        # No, restoring is hard because we lost the highlighting colors if we reset font?
        # Actually, setting Font.Name doesn't remove Color.
        
        # BUT, setting Font.Name to Times New Roman will make code look bad.
        
        # Better Strategy:
        # Select All -> Set Font.
        # Then Loop through paragraphs. If it has shading (Code Block), set font back to Consolas.
        
        # Step 1: Global Reset (Fastest way to fix Chinese fonts)
        word.Selection.WholeStory()
        word.Selection.Font.NameFarEast = "宋体"
        word.Selection.Font.NameAscii = "Times New Roman"
        word.Selection.Font.NameOther = "Times New Roman"
        
        # Step 2: Restore Code Blocks (Consolas)
        print("Restoring Code Block Fonts (Consolas)...")
        # Optimization: Use Find to search for paragraphs with Shading?
        # Iterate all paragraphs is safer for now.
        for p in doc.Paragraphs:
            # Check for black background (Shading)
            # wdTextureNone = 0. If it has texture/color, it's likely our code block.
            if p.Shading.BackgroundPatternColor == 0: # 0 is Black (0x000000) for us? 
                # Wait, Word colors are tricky. Automatic is -16777216? 
                # In convert script we set fill='000000'.
                # Let's check Shading.Texture or BackgroundPatternColor
                
                # If we set style='No Spacing', maybe check style?
                # But 'No Spacing' is used for code only in our script.
                if p.Style.NameLocal == "No Spacing" or p.Style.NameLocal == "无间隔":
                     p.Range.Font.NameAscii = "Consolas"
                     p.Range.Font.NameOther = "Consolas"
                     p.Range.Font.Name = "Consolas"
                     # Ensure spacing is tight
                     p.Format.SpaceAfter = 0
                     p.Format.SpaceBefore = 0
        
        # 2. Fix Headings specifically (Styles often persist)
        print("Refining Heading Styles to '黑体'...")
        for i in range(1, 4):
            try:
                # WPS compatible style access
                style_name = f"Heading {i}"
                try:
                    style = doc.Styles(style_name)
                except:
                    # Try Chinese localized names just in case
                    style_name_cn = f"标题 {i}"
                    style = doc.Styles(style_name_cn)
                
                style.Font.NameFarEast = "黑体"
                style.Font.NameAscii = "Arial" 
                style.Font.Name = "Arial"
            except Exception as e:
                print(f"Warning: Could not enable Heading {i} style fix: {e}")

        # --- TOC Updates ---
        # Search for placeholder again just in case previous attempts failed
        rng = doc.Content
        if rng.Find.Execute(FindText="[此处将自动生成正式目录]"):
             rng.Select()
             word.Selection.Delete()
             doc.TablesOfContents.Add(Range=word.Selection.Range, RightAlignPageNumbers=True, 
                                     UseHeadingStyles=True, UpperHeadingLevel=1, LowerHeadingLevel=3,
                                     IncludePageNumbers=True)

        if doc.TablesOfContents.Count > 0:
            doc.TablesOfContents(1).Update()
        
        doc.Fields.Update()
        
        # Save the fixed DOCX
        doc.Save()
        
        # Export PDF
        print(f"Exporting final PDF to {abs_pdf}...")
        doc.SaveAs(abs_pdf, FileFormat=17) # wdFormatPDF
        
        print("Success! Report finalized.")
        doc.Close()
        
    except Exception as e:
        print(f"CRITICAL ERROR during finalization: {e}")
        # Keep word open if error so user can see it? No, better close to avoid zombies.
        # doc.Close(SaveChanges=False)
        
    finally:
        try:
            word.Quit()
        except:
            pass

if __name__ == "__main__":
    docx = r"C:\Users\weirui\Desktop\AI_Test\AI辅助白内障筛查实践报告_最终排版.docx"
    pdf = r"C:\Users\weirui\Desktop\AI_Test\AI辅助白内障筛查实践报告_最终版.pdf"
    
    finalize_report(docx, pdf)
