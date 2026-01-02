
import os
import zipfile

def zip_dashboard(source_dir, output_filename):
    """
    Zips the contents of the dashboard directory, excluding backup folders.
    """
    with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            # Modify dirs in-place to skip backup folders
            if 'error_images_backup_23cases' in dirs:
                dirs.remove('error_images_backup_23cases')
            
            for file in files:
                file_path = os.path.join(root, file)
                # Calculate relative path for the zip archive
                # We want the structure inside the zip to start relatively, e.g. index.html at root
                arcname = os.path.relpath(file_path, start=source_dir)
                zipf.write(file_path, arcname)
    
    print(f"Dashboard packaged successfully into {output_filename}")

if __name__ == "__main__":
    source = r"C:\Users\weirui\Desktop\AI_Test\04visualization"
    output = r"C:\Users\weirui\Desktop\AI_Test\visualization_package.zip"
    zip_dashboard(source, output)
