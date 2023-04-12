import re
from oracle import cpp_oracle

def extract_functions_and_classes(file_path):
    with open(file_path, 'r') as f:
        content = f.read()

    # Match functions and short class definitions
    pattern = re.compile(r'\b(?:class|void|bool|int|float|double|char|short|long|string)\s+\w+\s*'
                         r'(?:<[^>]*>)?\s*\(.*?\)\s*\{[^{}]*?\}|'
                         r'\bclass\s+\w+\s*(?:[:]\s*[^{]*?)?\s*\{[^{}]*?\}', re.MULTILINE | re.DOTALL)

    return pattern.findall(content)

def airate_cpp(file_path, node="localhost", port=5000):
    markdown_str = ""
    code_blocks = extract_functions_and_classes(file_path)

    for idx, code_block in enumerate(code_blocks):
        score = cpp_oracle(code_block, node=node, port=port)
        markdown_str += f"\n  - Code block {idx + 1}:\n"
        markdown_str += f"    ```cpp\n{code_block.strip()}\n    ```\n"
        markdown_str += f"    Score: {score:.2f}\n"

    return markdown_str
