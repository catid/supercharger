import ast
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

def check_error_line(code):
    try:
        ast.parse(code)
    except Exception as e:
        return e.lineno
    return None

def indent_line(code, line_number, delta=1):
    lines = code.split('\n')
    error_line = lines[line_number - 1]

    current_indent_level = len(error_line) - len(error_line.lstrip())

    new_indent_level = current_indent_level + delta

    # Add correct indentation to the problematic line
    fixed_line = ' ' * new_indent_level + error_line.lstrip()
    lines[line_number - 1] = fixed_line

    # Update the code
    code = '\n'.join(lines)

    return code

def try_indenting(code, line_number, delta=1):
    orig_code = code
    for i in range(1, 8):
        code = indent_line(code, line_number, delta=delta)
        error_line = check_error_line(code)
        if error_line is None or error_line != line_number:
            return True, code
    return False, orig_code

def try_adding_colon(code, line_number):
    orig_code = code

    lines = code.split('\n')
    error_line = lines[line_number - 1]

    error_line += ":"

    lines[line_number - 1] = error_line

    code = '\n'.join(lines)

    #print(f"MODIFIED CODE: {code}")

    error_line = check_error_line(code)

    if error_line is None or error_line != line_number:
        return True, code
    return False, orig_code

def fix_ast_errors(code, max_attempts=100, expandtabs=True, delete_on_error=True):
    median_tab_spaces = detect_median_indentation(code)
    if median_tab_spaces <= 1:
        median_tab_spaces = 4

    if expandtabs:
        code = code.expandtabs(median_tab_spaces)

    attempts = 0

    while attempts < max_attempts:
        try_indent = True
        try_unindent = True
        try_colon = False
        lineno = 0

        try:
            ast.parse(code)
            break
        except SyntaxError as e:
            lineno = e.lineno
            #print("SYNTAX ERROR: {}".format(e))
            #print("CODE:\n---\n{}\n---\n".format(code))
            if "expected ':'" in e.msg:
                try_colon = True
                try_unindent = False
                try_indent = False
        except IndentationError as e:
            lineno = e.lineno
            #print("INDENT ERROR: {}".format(e))
            #print("CODE:\n---\n{}\n---\n".format(code))
            if "expected an indented block" in e.msg:
                try_unindent = False
            elif "unexpected indent" in e.msg or "unindent does not match" in e.msg:
                try_indent = False
        except Exception as e:
            lineno = e.lineno
            #print("OTHER ERROR: {}".format(e))
            #print("CODE:\n---\n{}\n---\n".format(code))

        if lineno == 0:
            break

        if try_colon:
            r, code = try_adding_colon(code, lineno)
            if r:
                continue

        if try_indent:
            r, code = try_indenting(code, lineno, delta=1)
            if r:
                continue
        if try_unindent:
            r, code = try_indenting(code, lineno, delta=-1)
            if r:
                continue

        # Give up if we can't fix the error and don't want to delete the code
        if not delete_on_error:
            break

        # Delete the line that caused the error
        lines = code.split('\n')
        del lines[lineno - 1]
        code = '\n'.join(lines)

        attempts += 1

    return code
