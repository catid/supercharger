# Use modules from parent folder
import os, sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

import logging

from server.client import ask_server
from prompts.ask_templates import ask_python_function_prototype
from clean_code import clean_code

def auto_pyfunc(comments, prototype, node="localhost", port=5000, temperature=1.0, max_tokens=1024):
    logging.debug(f"auto_pyfunc: comments = `{comments}`")
    logging.debug(f"auto_pyfunc: prototype = `{prototype}`")

    prompt, stop_strs = ask_python_function_prototype(comments, prototype)
    result = ask_server(prompt, stop_strs, node, port, temperature, max_tokens)
    code = clean_code(result)

    logging.debug(f"auto_pyfunc: code = \n{code}")

    if len(code) > 0:
        # Prepend the comments
        result = '\n'.join(comments.splitlines() + result.splitlines())

    return result
