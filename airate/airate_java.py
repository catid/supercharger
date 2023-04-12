import re
from oracle import java_oracle

def extract_methods(file_path):
    """
    Extracts all methods in a given Java file.
    Returns a dictionary with method names as keys and method code blocks as values.
    """
    with open(file_path) as f:
        code = f.read()

    methods = {}
    pattern = re.compile(r'((public|private|protected|static|final|synchronized|native|\s)*[\w\<\>\[\]]+\s+(\w+)\s*\(.*?\)\s*(throws\s+\w+\s*)?\{[^{}]*\})', re.DOTALL)
    for match in pattern.findall(code):
        method = match[0].strip()
        method_name = match[2]
        methods[method_name] = method

    return methods

def airate_java(file_path, node="localhost", port=5000):
    markdown_str = ""
    code_blocks = extract_methods(file_path)

    for idx, code_block in enumerate(code_blocks):
        score = java_oracle(code_block, node=node, port=port)
        markdown_str += f"\n  - Code block {idx + 1}:\n"
        markdown_str += f"    ```java\n{code_block.strip()}\n    ```\n"
        markdown_str += f"    Score: {score:.2f}\n"

    return markdown_str
