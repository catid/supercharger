import re
import ast
import logging

import autopep8
import black

# Remove everything outside the first ``` code block containing a function.
def parse_code_blocks(input_text):
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

def only_defs_and_imports(code_string, func_name_to_exclude=None):
    tree = ast.parse(code_string)
    filtered_nodes = []

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.FunctionDef):
            filtered_nodes.append(node)
        elif isinstance(node, ast.Import):
            filtered_names = [name for name in node.names if not (name.name.split('.')[0] == func_name_to_exclude)]
            if filtered_names:
                node.names = filtered_names
                filtered_nodes.append(node)
        elif isinstance(node, ast.ImportFrom):
            filtered_names = [name for name in node.names if name.name != func_name_to_exclude]
            if filtered_names:
                node.names = filtered_names
                filtered_nodes.append(node)

    return ast.unparse(filtered_nodes)

def clean_code(code):
    # Use autopep8 to automatically fix simple errors.
    try:
        fixed = autopep8.fix_code(code, options={'aggressive': 0})
        logging.debug(f"fixed:\n{fixed}\n")
        if len(fixed) > 0:
            code = fixed
    except Exception as e:
        logging.debug(f"clean_code::autopep8.fix_code failed due to exception: {e}")

    # Use black to automatically clean up the code.
    try:
        formatted_code = black.format_file_contents(code, fast=False, mode=black.Mode())
        logging.debug(f"formatted_code:\n{formatted_code}\n")
        if len(formatted_code) > 0:
            code = formatted_code
    except Exception as e:
        logging.debug(f"clean_code::black.format_file_contents failed due to exception: {e}")

    return code


# Get any import lines
def get_imports(code_string):
    # Split the code string into lines
    lines = code_string.strip().split('\n')
    # Filter out any lines that don't start with "import" or "from"
    import_lines = list(filter(lambda x: x.strip().startswith(('import', 'from')), lines))
    # Return the list of import lines
    return import_lines

# Return the first function and its imports, removing any comments
def find_first_function(py_string):
    # remove all comments
    py_string = re.sub(r'#.*', '', py_string)
    # remove all multi-line strings delimited by """ or '''
    py_string = re.sub(r'(""".*?""")|(\'\'\'.*?\'\'\')', '', py_string, flags=re.DOTALL)
    # split the string into lines
    lines = py_string.split('\n')
    # initialize a list to hold the function lines
    function_lines = []
    # initialize a flag to indicate whether we've found the first function
    found_function = False
    # iterate over the lines in regular order
    for line in lines:
        # if we haven't found the first function and we encounter a line that starts with "def"
        if not found_function and line.strip().startswith('def '):
            # set the flag and remember the current indentation level
            found_function = True
            indent = len(line) - len(line.lstrip())
            function_lines.append(line)
        # if we've found the first function and we encounter a line with higher indentation
        elif found_function and (len(line) - len(line.lstrip()) > indent):
            # add this line to the list of function lines
            function_lines.append(line)
        # if we've found the first function and we encounter a line with lower indentation
        elif found_function and len(line) - len(line.lstrip()) < indent:
            # we've reached the end of the function, so break out of the loop
            break
    # join the function lines into a single string
    function_string = '\n'.join(function_lines)
    # Get the import lines above the first function
    import_lines = get_imports('\n'.join(lines[:lines.index(function_lines[0])]))
    # return the function string and the import lines
    return '\n'.join(import_lines + function_lines)
