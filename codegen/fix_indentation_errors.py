import re

import re
from statistics import median

def detect_median_indentation(code):
    indentation_counts = []
    in_comment = False
    for line in code.split('\n'):
        # Check if line starts with comment
        if re.match(r'^\s*#', line):
            continue
        # Check if line contains multi-line comment start
        elif re.match(r'^\s*""".*"""\s*$', line):
            continue
        elif re.match(r'^\s*""".*', line):
            in_comment = True
        # Check if line contains multi-line comment end
        elif re.match(r'.*""".*$', line):
            in_comment = False
        # If not in multi-line comment, count the indentation level
        elif not in_comment:
            indentation_counts.append(len(line) - len(line.lstrip()))

    if len(indentation_counts) > 0:
        median_indentation = int(median(indentation_counts))
    else:
        median_indentation = 0

    return median_indentation

def fix_indentation_errors(code, expandtabs=True):
    """Fixes indentation errors in Python code"""

    if expandtabs:
        median_tab_spaces = detect_median_indentation(code)
        if median_tab_spaces <= 1:
            median_tab_spaces = 4
        code = code.expandtabs(median_tab_spaces)

    # Split the code into lines
    lines = code.split('\n')

    # Initialize variables
    indent_level = 0
    prev_indent_level = 0
    fixed_lines = []
    keyword_indented = False

    # FIX: Handle defining JSON or Array/List
    # FIX: Handle function call on multiple lines
    # FIX: Handle multi-line strings

    # Loop through each line of code
    for line in lines:
        stripped_line = line.strip()

        # Skip blank lines
        if not stripped_line:
            fixed_lines.append(stripped_line)
            continue

        # Determine the current indentation level
        current_indent_level = len(line) - len(stripped_line)
        delta_indent = current_indent_level - prev_indent_level
        prev_indent_level = current_indent_level

        # Fix the indentation if necessary
        if stripped_line.startswith(('def ', 'if ', 'for ', 'while ', 'try:', 'class ', 'with ')):
            fixed_lines.append(' ' * indent_level + stripped_line)
            indent_level += 4
            keyword_indented = True
        elif stripped_line.startswith(('else:', 'elif ', 'except ', 'except:', 'finally:')):
            fixed_lines.append(' ' * (indent_level - 4) + stripped_line)
        else:
            if delta_indent <= -2:
                # Lost indentation in original
                indent_level -= 4
                if indent_level < 0:
                    indent_level = 0

            fixed_lines.append(' ' * indent_level + stripped_line)

        keyword_indented = False

    # Join the fixed lines and return the result
    return '\n'.join(fixed_lines)
