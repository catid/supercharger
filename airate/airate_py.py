import ast
from oracle import py_oracle

def extract_functions_and_classes(file_path):
    with open(file_path, 'r') as f:
        content = f.read()

    try:
        tree = ast.parse(content)
    except SyntaxError:
        print(f"Error: Failed to parse {file_path}")
        return []

    functions_and_classes = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            start_line = node.lineno - 1
            end_line = max([item.lineno for item in ast.walk(node) if isinstance(item, ast.Expr)], default=start_line)
            functions_and_classes.append('\n'.join(content.splitlines()[start_line:end_line + 1]))

    return functions_and_classes

def airate_py(file_path):
    markdown_str = ""
    code_blocks = extract_functions_and_classes(file_path)

    for idx, code_block in enumerate(code_blocks):
        score = py_oracle(code_block)
        markdown_str += f"\n  - Code block {idx + 1}:\n"
        markdown_str += f"    ```python\n{code_block.strip()}\n    ```\n"
        markdown_str += f"    Score: {score:.2f}\n"

    return markdown_str
