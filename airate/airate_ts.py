import re
from oracle import ts_oracle

def extract_functions_and_classes(file_path: str) -> list[str]:
    with open(file_path, "r") as file:
        code = file.read()
    pattern = r"((async\s+)?function\s+\w+\s*\(.*?\)\s*\{(?:[^{}]*?\{[^{}]*?\}[^{}]*?)*?\}|class\s+\w+\s*\{[\s\S]*?\})"
    matches = re.findall(pattern, code, re.MULTILINE)
    return matches

def airate_ts(file_path, node="localhost", port=5000):
    markdown_str = ""
    code_blocks = extract_functions_and_classes(file_path)

    for idx, code_block in enumerate(code_blocks):
        score = ts_oracle(code_block, node=node, port=port)
        markdown_str += f"\n  - Code block {idx + 1}:\n"
        markdown_str += f"    ```typescript\n{code_block.strip()}\n    ```\n"
        markdown_str += f"    Score: {score:.2f}\n"

        print(f"Code block {idx + 1} score: {score:.2f}")

    return markdown_str
