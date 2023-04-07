import re

def fix_indentation(code_string):
    lines = code_string.split("\n")
    fixed_lines = []

    indent_level = 0
    prev_line_indent = 0
    if_stack = []

    for line in lines:
        stripped_line = line.lstrip()
        if not stripped_line:
            # Empty line, keep it as it is
            fixed_lines.append(line)
            continue

        current_indent = len(line) - len(stripped_line)
        if re.match(r"(elif|else)\b", stripped_line):
            indent_level = if_stack[-1] if if_stack else 0
        elif stripped_line.endswith(":"):
            indent_level = prev_line_indent
            if re.match(r"if\b", stripped_line):
                if_stack.append(indent_level)
        else:
            indent_level = max(0, indent_level)

        if re.match(r"(def|class)\b", stripped_line):
            fixed_line = " " * prev_line_indent + stripped_line
        else:
            fixed_line = " " * indent_level + stripped_line

        fixed_lines.append(fixed_line)

        prev_line_indent = indent_level

        # Update indent_level for next line
        if stripped_line.endswith(":") and not re.match(r"(elif|else)\b", stripped_line):
            indent_level += 4

    return "\n".join(fixed_lines)

# Example usage:
input_code = """
   def my_function(a, b):
       if a > b:
            print("a is greater than b")
            elif a < b:
                print("a is less than b")
            else:
                    print("a is equal to b")
"""

fixed_code = fix_indentation(input_code)
print(fixed_code)
