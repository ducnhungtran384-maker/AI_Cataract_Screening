
import os
import re

JS_FILE = r"c:\Users\weirui\Desktop\AI_Test\visualization\js\data.js"

def patch_data():
    if not os.path.exists(JS_FILE):
        print(f"File not found: {JS_FILE}")
        return

    with open(JS_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    
    # Regex to extract key-value pairs like "key": value
    re_kv = re.compile(r'"(\w+)":\s*([0-9\.]+)')
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Check start of a subgroup block
        if '"cataract": {' in line or '"normal": {' in line:
            # We found a block. We need to process this block.
            # We'll read lines until we find the closing brace line.
            # While reading, we'll store lines and values.
            
            block_lines = [line]
            precision = None
            recall = None
            has_accuracy = False
            has_f1 = False
            
            j = i + 1
            while j < len(lines):
                sub_line = lines[j]
                
                # Check for end of block (assuming indentation or single brace)
                # Being safe: check if line contains just closing brace, possibly with comma
                if sub_line.strip() in ['}', '},']:
                    # Block ends here
                    
                    # Calculate if needed
                    if precision is not None and recall is not None:
                         # Calculate metrics
                         accuracy = recall
                         if (precision + recall) > 0:
                             f1 = 2 * precision * recall / (precision + recall)
                         else:
                             f1 = 0.0
                             
                         # Insert if missing
                         # We insert before the closing brace (sub_line)
                         # Add comma to the last line of content if it doesn't have one
                         last_content_line = block_lines[-1]
                         if not last_content_line.strip().replace('\n','').endswith(','):
                             block_lines[-1] = last_content_line.rstrip() + ",\n"
                             
                         if not has_accuracy:
                             block_lines.append(f'      "accuracy": {round(accuracy, 4)},\n')
                         if not has_f1:
                             block_lines.append(f'      "f1": {round(f1, 4)},\n')
                    
                    block_lines.append(sub_line)
                    new_lines.extend(block_lines)
                    i = j + 1
                    break
                
                # Parse metrics
                m = re_kv.search(sub_line)
                if m:
                    key, val = m.groups()
                    if key == 'precision': precision = float(val)
                    elif key == 'recall': recall = float(val)
                    elif key == 'accuracy': has_accuracy = True
                    elif key == 'f1': has_f1 = True
                
                block_lines.append(sub_line)
                j += 1
            else:
                # Loop finished without finding closing brace? (Unexpected EOF inside block)
                # Just append what we have
                new_lines.extend(block_lines)
                i = j
                
        else:
            new_lines.append(line)
            i += 1
            
    # Write back
    with open(JS_FILE, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print("Patch complete (Robust Mode).")

if __name__ == "__main__":
    patch_data()
