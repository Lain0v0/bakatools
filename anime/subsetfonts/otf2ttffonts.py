import os
import subprocess
import shutil
import sys

def convert_otf_to_ttf(file_path):
    try:
        # Run the otf2ttf command
        result = subprocess.run(['otf2ttf', file_path], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error converting {file_path}: {result.stderr}")
            return False
        print(f"Successfully converted {file_path}")
        
        # Construct the expected output file path
        base_name = os.path.splitext(file_path)[0]
        output_file = f"{base_name}.ttf"
        print(f"Constructed output file path: {output_file}")
        
        # Check if the output file exists
        if os.path.exists(output_file):
            print(f"Output file exists: {output_file}")
            destination_dir = r"D:\Fonts\All\outputs"  # 转换输出位置
            shutil.move(output_file, os.path.join(destination_dir, os.path.basename(output_file)))
            print(f"Successfully moved {output_file} to {destination_dir}")
            return True
        else:
            print(f"Error: {output_file} not found.")
            return False
    except Exception as e:
        print(f"Exception occurred: {e}")
        return False

def process_folder(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith('.otf'):
                file_path = os.path.join(root, file)
                convert_otf_to_ttf(file_path)

def main():
    if len(sys.argv) < 2:
        print("No folders were provided.")
        return
    
    folders = sys.argv[1:]
    
    for folder in folders:
        process_folder(folder)

if __name__ == "__main__":
    main()
