import re

def fix_missing_colons(code_string):
    lines = code_string.split('\n')
    fixed_lines = []

    for line in lines:
        line = re.sub(r'\b(def|if|elif|else|for|while|with|class)\b(.*)(?<!:)\s*$', r'\1\2:', line)
        fixed_lines.append(line)

    return '\n'.join(fixed_lines)
