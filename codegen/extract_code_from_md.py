# Remove everything outside the first ``` code block containing a function.
def extract_code_from_md(input_text):
    output = []
    code_block = False
    found_def = False
    for line in input_text.splitlines():
        if line.strip().startswith("```"):
            if found_def:
                break
            code_block = not code_block
            if code_block:
                found_def = False
            output.clear()
        elif code_block:
            output.append(line)
            if 'def' in line:
                found_def = True
    return '\n'.join(output)
