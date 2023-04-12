import re
from oracle import js_oracle

def extract_functions_and_classes(file_path):
    with open(file_path, 'r') as f:
        content = f.read()

    # Match functions and short class definitions
    pattern = re.compile(r'(?:(?:async\s+)?function\s+\w+\s*\(.*?\)\s*\{(?:[^{}]*?\{[^{}]*?\}[^{}]*?)*?\}|'
                        r'(?:class\s+\w+\s*(?:extends\s+\w+)?\s*\{(?:[^{}]*?\{[^{}]*?\}[^{}]*?)*?\}))',
                        re.MULTILINE | re.DOTALL)

    return pattern.findall(content)

def airate_js(file_path):
    markdown_str = ""
    code_blocks = extract_functions_and_classes(file_path)

    for idx, code_block in enumerate(code_blocks):
        score = js_oracle(code_block)
        markdown_str += f"\n  - Code block {idx + 1}:\n"
        markdown_str += f"    ```javascript\n{code_block.strip()}\n    ```\n"
        markdown_str += f"    Score: {score:.2f}\n"

    return markdown_str
