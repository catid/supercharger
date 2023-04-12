import re
from oracle import php_oracle

def extract_functions(file_contents: str):
    function_regex = r"function\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\("
    functions = re.findall(function_regex, file_contents)
    return functions

def airate_php(file_path, node="localhost", port=5000):
    markdown_str = ""
    code_blocks = extract_functions(file_path)

    for idx, code_block in enumerate(code_blocks):
        score = php_oracle(code_block, node=node, port=port)
        markdown_str += f"\n  - Code block {idx + 1}:\n"
        markdown_str += f"    ```php\n{code_block.strip()}\n    ```\n"
        markdown_str += f"    Score: {score:.2f}\n"

    return markdown_str
