import re
import ast
import logging

from yapf.yapflib.yapf_api import FormatCode

from fix_mismatched_delimiters import fix_mismatched_delimiters
from fix_ast_errors import fix_ast_errors
from extract_code_from_md import extract_code_from_md

# If you only expect a Python function and nothing else but imports this can clean the junk after syntax errors are cleaned up
def only_defs_and_imports(code_string, func_name_to_exclude=None):
    # This will fail if the input code is not valid Python
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

def clean_code(code, strip_md=True, strip_globals=True):

    print(f"CODE:\n\n----\n{code}\n----\n\n")

    if strip_md:
        try:
            code = extract_code_from_md(code)
        except Exception as e:
            logging.info(f"clean_code::extract_code_from_md failed due to exception: {e}")

    print(f"extract_code_from_md:\n\n----\n{code}\n----\n\n")

    try:
        code = fix_mismatched_delimiters(code)
    except Exception as e:
        logging.info(f"clean_code::fix_mismatched_delimiters failed due to exception: {e}")

    print(f"fix_mismatched_delimiters:\n\n----\n{code}\n----\n\n")

    try:
        code = fix_ast_errors(code)
    except Exception as e:
        logging.info(f"clean_code::fix_ast_errors failed due to exception: {e}")

    print(f"fix_ast_errors:\n\n----\n{code}\n----\n\n")

    if strip_globals:
        try:
            code = only_defs_and_imports(code)
        except Exception as e:
            logging.info(f"clean_code::only_defs_and_imports failed due to exception: {e}")

    print(f"only_defs_and_imports:\n\n----\n{code}\n----\n\n")

    try:
        code, _ = FormatCode(code)
    except Exception as e:
        logging.info(f"clean_code::yapf failed due to exception: {e}")
        return code, False

    print(f"FormatCode:\n\n----\n{code}\n----\n\n")

    return code, True
