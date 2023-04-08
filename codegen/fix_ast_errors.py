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

def check_error(code):
    try:
        ast.parse(code)
    except Exception as e:
        return e
    return None

def indent_line(code, e, delta=1):
    lines = code.split('\n')
    error_line = lines[e.lineno - 1]

    current_indent_level = len(error_line) - len(error_line.lstrip())

    new_indent_level = current_indent_level + delta

    # Add correct indentation to the problematic line
    fixed_line = ' ' * new_indent_level + error_line.lstrip()
    lines[e.lineno - 1] = fixed_line

    # Update the code
    code = '\n'.join(lines)

    return code

def try_indenting(code, e, delta=1):
    orig_code = code
    for i in range(1, 8):
        code = indent_line(code, e, delta=delta)
        ne = check_error(code)
        if ne is None or ne.lineno != e.lineno:
            return True, code
    return False, orig_code

def try_adding_colon(code, e):
    orig_code = code

    lines = code.split('\n')
    error_line = lines[e.lineno - 1]

    error_line += ":"

    lines[e.lineno - 1] = error_line

    code = '\n'.join(lines)

    #print(f"MODIFIED CODE: {code}")

    ne = check_error(code)

    if ne is None or ne.lineno != e.lineno:
        return True, code
    return False, orig_code

def close_line(code, lineno, delim=")", start=True):
    lines = code.split('\n')
    error_line = lines[lineno - 1]

    if start:
        error_line = delim + error_line
    else:
        error_line += delim

    lines[lineno - 1] = error_line

    code = '\n'.join(lines)

    return code

def try_closing_delim(code, e, delim):
    orig_code = code
    try:
        for i in range(100):
            if i > 0:
                code = close_line(code, e.lineno + i, delim=delim, start=True)
                #print("try_closing_delim CODE: {}".format(code))
                ne = check_error(code)
                #print("try_closing_delim NE: {}".format(ne))
                if ne is None or ne.lineno != e.lineno or str(ne) != str(e):
                    return True, code

            code = close_line(code, e.lineno + i, delim=delim, start=False)
            #print("try_closing_delim CODE: {}".format(code))
            ne = check_error(code)
            #print("try_closing_delim NE: {}".format(ne))
            if ne is None or ne.lineno != e.lineno or str(ne) != str(e):
                return True, code
    except Exception as e:
        pass
    return False, orig_code

def extract_mismatched_delimiters(error_message):
    pattern = r"closing parenthesis '(\S)' does not match opening parenthesis '(\S)'"
    match = re.search(pattern, error_message)

    if match:
        closing_char, opening_char = match.groups()
        return closing_char, opening_char
    else:
        return None

def replace_final_closing_char(input_string, closing_char, opening_char):
    last_closing_index = input_string.rfind(closing_char)
    if last_closing_index != -1:
        input_string = input_string[:last_closing_index] + opening_char + input_string[last_closing_index + 1:]
    return input_string

def flip_opening_delimiters(input_string):
    opening_chars = "{[("
    closing_chars = "}])"
    delimiter_map = dict(zip(opening_chars, closing_chars))

    for opening, closing in delimiter_map.items():
        input_string = input_string.replace(opening, closing)

    return input_string

def try_replacing_closing_with_opening(code, e, closing_char, opening_char):
    orig_code = code

    lines = code.split('\n')
    error_line = lines[e.lineno - 1]

    error_line = replace_final_closing_char(error_line, closing_char, opening_char)

    lines[e.lineno - 1] = error_line

    code = '\n'.join(lines)

    ne = check_error(code)

    if ne is None or ne.lineno != e.lineno or str(ne) != str(e):
        return True, code
    return False, orig_code

def parse_unbalanced_paren(error_message):
    match = re.search(r"'(\(|\)|\[|\]|\{|\})' was never closed", error_message)
    if match:
        return match.group(1)
    return None

def fix_ast_errors(code, max_attempts=100, expandtabs=True, delete_on_error=True):
    median_tab_spaces = detect_median_indentation(code)
    if median_tab_spaces <= 1:
        median_tab_spaces = 4

    if expandtabs:
        code = code.expandtabs(median_tab_spaces)

    attempts = 0

    while attempts < max_attempts:
        try_indent = False
        try_unindent = False
        close_delim = None
        error = None

        try:
            ast.parse(code)
            break
        except SyntaxError as e:
            error = e
            print("SYNTAX ERROR: {}".format(e))
            print("CODE:\n---\n{}\n---\n".format(code))
            if "expected ':'" in e.msg:
                r, code = try_adding_colon(code, e)
                if r: continue
            elif "was never closed" in e.msg:
                close_delim = parse_unbalanced_paren(e.msg)
                if close_delim:
                    r, code = try_closing_delim(code, error, flip_opening_delimiters(close_delim))
                    if r: continue
            elif "does not match opening parenthesis" in e.msg:
                closing, opening = extract_mismatched_delimiters(e.msg)
                r, code = try_replacing_closing_with_opening(code, e, closing, flip_opening_delimiters(opening))
                if r: continue
        except IndentationError as e:
            error = e
            print("INDENT ERROR: {}".format(e))
            print("CODE:\n---\n{}\n---\n".format(code))
            if "expected an indented block" in e.msg:
                try_indent = True
            elif "unexpected indent" in e.msg or "unindent does not match" in e.msg:
                try_unindent = True
        except Exception as e:
            error = e
            try_indent = True
            try_unindent = True
            print("OTHER ERROR: {}".format(e))
            print("CODE:\n---\n{}\n---\n".format(code))

        if error is None:
            break

        if try_indent:
            r, code = try_indenting(code, error, delta=1)
            if r: continue
        if try_unindent:
            r, code = try_indenting(code, error, delta=-1)
            if r: continue

        # Give up if we can't fix the error and don't want to delete the code
        if not delete_on_error:
            break

        print("FAILED TO FIX ERROR: {}".format(error))

        # Delete the line that caused the error
        lines = code.split('\n')
        del lines[error.lineno - 1]
        code = '\n'.join(lines)

        attempts += 1

    return code
