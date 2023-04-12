import re
import ast
import logging

from yapf.yapflib.yapf_api import FormatCode

from fix_ast_errors import fix_ast_errors
from extract_code_from_md import extract_code_from_md

# If you only expect a Python function and nothing else but imports this can clean the junk after syntax errors are cleaned up
def only_defs_and_imports(code_string, strip_import_mods=[], strip_import_funcs=[]):
    # This will fail if the input code is not valid Python
    tree = ast.parse(code_string)
    filtered_nodes = []

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.FunctionDef):
            filtered_nodes.append(node)
        elif isinstance(node, ast.Import):
            filtered_names = [name for name in node.names if not name.name in strip_import_mods]
            if filtered_names:
                node.names = filtered_names
                filtered_nodes.append(node)
        elif isinstance(node, ast.ImportFrom):
            if node.module not in strip_import_mods:
                filtered_names = [name for name in node.names if not name.name in strip_import_funcs]
                if filtered_names:
                    node.names = filtered_names
                    filtered_nodes.append(node)

    return ast.unparse(filtered_nodes)

def remove_comments_before_first_function(script):
    # Match function definition pattern
    function_pattern = re.compile(r'^def .*\(', re.MULTILINE)
    
    # Find the index of the first function definition
    match = function_pattern.search(script)
    if match:
        start_index = match.start()
    else:
        # If there's no function definition, return the original script
        return script
    
    # Remove line comments
    line_comment_pattern = re.compile(r'(?<=\n)#.*\n', re.MULTILINE)
    clean_script = line_comment_pattern.sub('\n', script[:start_index])

    # Remove multi-line comments
    multiline_comment_pattern = re.compile(r'("""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\')', re.MULTILINE)
    clean_script = multiline_comment_pattern.sub('', clean_script)

    # Add the remaining script after the first function definition
    clean_script += script[start_index:]

    return clean_script

def clean_code(code, strip_md=True, strip_globals=True, strip_leading_comments=False, strip_import_mods=[], strip_import_funcs=[], add_smart_imports=True):

    #print(f"CODE:\n\n----\n{code}\n----\n\n")

    if strip_md:
        try:
            code = extract_code_from_md(code)
        except Exception as e:
            logging.info(f"clean_code::extract_code_from_md failed due to exception: {e}")

    #print(f"extract_code_from_md:\n\n----\n{code}\n----\n\n")

    try:
        code = fix_ast_errors(code)
    except Exception as e:
        logging.info(f"clean_code::fix_ast_errors failed due to exception: {e}")

    #print(f"fix_ast_errors:\n\n----\n{code}\n----\n\n")

    if strip_globals:
        try:
            code = only_defs_and_imports(code, strip_import_mods=strip_import_mods, strip_import_funcs=strip_import_funcs)
        except Exception as e:
            logging.info(f"clean_code::only_defs_and_imports failed due to exception: {e}")

    #print(f"only_defs_and_imports:\n\n----\n{code}\n----\n\n")

    if strip_leading_comments:
        try:
            code = remove_comments_before_first_function(code)
        except Exception as e:
            logging.info(f"clean_code::remove_comments_before_first_function failed due to exception: {e}")

    #print(f"remove_comments_before_first_function:\n\n----\n{code}\n----\n\n")

    # Use smart_imports to fix up any problems with forgetting imports
    if add_smart_imports and len(code.strip()) > 0:
        code = f"import smart_imports\nsmart_imports.all()\n{code}"

    try:
        code, _ = FormatCode(code)
    except Exception as e:
        logging.info(f"clean_code::yapf failed due to exception: {e}")
        return code, False

    #print(f"FormatCode:\n\n----\n{code}\n----\n\n")

    return code, True
