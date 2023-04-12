import sys

import clang.cindex
import ctypes.util

from oracle import cpp_oracle

already_setup = False

def setup_clang():
    # Only do it once
    global already_setup
    if already_setup:
        return
    already_setup = True

    # Find the Clang library file using ctypes.util.find_library()
    libclang_path = ctypes.util.find_library('clang')
    if not libclang_path:
        raise RuntimeError('Failed to find Clang library')

    # Set the path to the Clang library
    clang.cindex.Config.set_library_file(libclang_path)

def functions_in_file(cursor, file_path):
    if cursor.kind == clang.cindex.CursorKind.CXX_METHOD:
        if cursor.location.file and cursor.location.file.name == file_path:
            has_body = any(child.kind == clang.cindex.CursorKind.COMPOUND_STMT for child in cursor.get_children())
            if has_body:
                yield cursor

    if cursor.kind == clang.cindex.CursorKind.FUNCTION_DECL:
        if cursor.location.file and cursor.location.file.name == file_path:
            yield cursor

    for child in cursor.get_children():
        yield from functions_in_file(child, file_path)

def function_source(node, file_contents):
    extent = node.extent
    start, end = extent.start, extent.end
    func_src = file_contents[start.offset:end.offset]

    # Find comments leading up to the function
    lines = file_contents[:start.offset].splitlines()
    comments = []
    for line in reversed(lines):
        stripped = line.strip()
        if stripped.startswith("//") or stripped.startswith("/*") or stripped.endswith("*/"):
            comments.append(line)
        else:
            break

    comments.reverse()
    comment_str = "\n".join(comments)

    return f"{comment_str}\n{func_src}" if comments else func_src

def extract_functions(file_path):
    setup_clang()

    index = clang.cindex.Index.create()
    tu = index.parse(file_path)

    with open(file_path, 'r') as f:
        file_contents = f.read()

    code_blocks = []
    for func in functions_in_file(tu.cursor, file_path):
        code_blocks.append(function_source(func, file_contents))

    return code_blocks

def airate_cpp(file_path, node="localhost", port=5000):
    markdown_str = ""
    code_blocks = extract_functions(file_path)

    for idx, code_block in enumerate(code_blocks):
        score = cpp_oracle(code_block, node=node, port=port)
        markdown_str += f"\n  - Code block {idx + 1}:\n"
        markdown_str += f"    ```cpp\n{code_block.strip()}\n    ```\n"
        markdown_str += f"    Score: {score:.2f}\n"

    return markdown_str
