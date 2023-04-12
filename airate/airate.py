import argparse
import os
from pathlib import Path

# Import the airate modules for each file type
import airate_cpp
import airate_py
import airate_js
import airate_ts
import airate_java
import airate_cs
import airate_php

file_handlers = {
    ".cpp": airate_cpp.airate_cpp,
    #".py": airate_py.airate_py,
    #".js": airate_js.airate_js,
    #".ts": airate_ts.airate_ts,
    #".java": airate_java.airate_java,
    #".cs": airate_cs.airate_cs,
    #".php": airate_php.airate_php,
}

def rate_file(args, file_path, depth):
    markdown_str = ""
    file_ext = Path(file_path).suffix

    if file_ext in file_handlers:
        handler = file_handlers[file_ext]
        markdown_str += f"{'  ' * depth}* {file_path}\n"
        markdown_str += handler(file_path, args.node, args.port)

    return markdown_str

def process_directory(args, path, depth=0):
    markdown_str = ""
    for entry in os.scandir(path):
        if entry.is_file():
            markdown_str += rate_file(args, entry.path, depth)
        elif entry.is_dir():
            markdown_str += f"{'  ' * depth}* {entry.name}/\n"
            markdown_str += process_directory(entry.path, depth + 1)

    return markdown_str

def main():
    parser = argparse.ArgumentParser(description="Recursively process files in a directory or a single file")
    parser.add_argument("path", help="Path to the directory or file")
    parser.add_argument("--node", type=str, default="localhost", help="Server port")
    parser.add_argument("--port", type=int, default=5000, help="Server port")

    args = parser.parse_args()
    path = args.path

    if os.path.isfile(path):
        print(rate_file(path, 0))
    elif os.path.isdir(path):
        print(process_directory(args, path))
    else:
        print(f"Error: {path} is not a valid file or directory")

if __name__ == "__main__":
    main()
