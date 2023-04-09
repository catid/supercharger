# Use modules from parent folder
import os, sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

import re
import logging

from server.client import ask_server
from prompts.ask_templates import ask_python_pytest_prototype, ask_python_function_prototype, ask_python_analyzer, ask_python_test_analyzer, ask_python_test_judge, ask_python_code_judge
from clean_code import clean_code

def autopy_func(comments, prototype, node="localhost", port=5000, temperature=1.0, max_tokens=1024):
    #logging.info(f"autopy_func: comments = `{comments}`")
    #logging.info(f"autopy_func: prototype = `{prototype}`")

    prompt, stop_strs = ask_python_function_prototype(comments, prototype)

    #logging.info(f"autopy_func: prompt = \n{prompt}")
    #logging.info(f"autopy_func: stop_strs = {stop_strs}")

    result = ask_server(prompt, stop_strs, node, port, temperature, max_tokens)

    #logging.info(f"autopy_func: result = \n{result}")

    code, _ = clean_code(result, strip_leading_comments=True)

    #logging.info(f"autopy_func: code = \n{code}")

    if len(code.strip()) > 0:
        # Prepend the comments
        code = '\n'.join(comments.splitlines() + code.splitlines())

    return code

def autopy_func_improve(comments, code, node="localhost", port=5000, temperature=1.0, max_tokens=1024):
    logging.info(f"autopy_func_analyze: comments = `{comments}`, prototype = `{code}`")

    prompt, stop_strs = ask_python_analyzer(code)

    logging.info(f"autopy_func_analyze: prompt = \n{prompt}")
    logging.info(f"autopy_func_analyze: stop_strs = {stop_strs}")

    result = ask_server(prompt, stop_strs, node, port, temperature, max_tokens)

    logging.info(f"autopy_func_analyze: result = \n{result}")

    code, _ = clean_code(result, strip_leading_comments=True)

    logging.info(f"autopy_func_analyze: code = \n{code}")

    if len(code.strip()) > 0:
        # Prepend the comments
        code = '\n'.join(comments.splitlines() + code.splitlines())

    return code

def autopy_test(comments, prototype, function_name, node="localhost", port=5000, temperature=1.0, max_tokens=1024):
    #logging.info(f"autopy_test: comments = `{comments}`, prototype = `{prototype}`")

    prompt, stop_strs = ask_python_pytest_prototype(comments, prototype)

    #logging.info(f"autopy_test: prompt = \n{prompt}")
    #logging.info(f"autopy_test: stop_strs = {stop_strs}")

    result = ask_server(prompt, stop_strs, node, port, temperature, max_tokens)

    #logging.info(f"autopy_test: result = \n{result}")

    code, _ = clean_code(result, strip_import_mods=["pytest"], strip_import_funcs=[function_name])

    #logging.debug(f"autopy_test: code = \n{code}")

    if len(code.strip()) > 0:
        # Prepend the required imports
        required_imports = ["import pytest", f"from {function_name} import {function_name}"]
        code = '\n'.join(required_imports + code.splitlines())

    return code

def autopy_test_improve(comments, prototype, function_name, test_code, node="localhost", port=5000, temperature=1.0, max_tokens=1024):
    #logging.info(f"autopy_test_analyze: comments = `{comments}`, prototype = `{prototype}`")

    prompt, stop_strs = ask_python_test_analyzer(comments, prototype, function_name, test_code)

    #logging.info(f"autopy_test_analyze: prompt = \n{prompt}")
    #logging.info(f"autopy_test_analyze: stop_strs = {stop_strs}")

    result = ask_server(prompt, stop_strs, node, port, temperature, max_tokens)

    #logging.info(f"autopy_test_analyze: result = \n{result}")

    code, _ = clean_code(result, strip_import_mods=["pytest"], strip_import_funcs=[function_name])

    #logging.info(f"autopy_test_analyze: code = \n{code}")

    if len(code.strip()) > 0:
        # Prepend the required imports
        required_imports = ["import pytest", f"from {function_name} import {function_name}"]
        code = '\n'.join(required_imports + code.splitlines())

    return code

def find_first_number_between_0_and_1(s: str):
    pattern = r'(?<![0-9.])0(\.\d+)?(?!\d)|(?<![0-9.])1(\.\d+)?(?!\d)'
    matches = re.finditer(pattern, s)
    
    for match in matches:
        start_index = match.start()
        if start_index == 0 or s[start_index - 1] != '-':
            f = float(match.group())
            if f >= 0 and f <= 1:
                return f

    return None

def autopy_code_judge(commented_code, function_name, node="localhost", port=5000, temperature=0.5, max_tokens=32):
    #logging.info(f"autopy_code_judge: comments = `{comments}`, prototype = `{prototype}`")

    prompt, stop_strs = ask_python_code_judge(commented_code, function_name)

    logging.info(f"autopy_code_judge: prompt = \n{prompt}")
    logging.info(f"autopy_code_judge: stop_strs = {stop_strs}")

    result = ask_server(prompt, stop_strs, node, port, temperature, max_tokens)

    logging.info(f"autopy_code_judge: result = \n{result}")

    return find_first_number_between_0_and_1(result)

def autopy_test_judge(commented_code, function_name, test_code, node="localhost", port=5000, temperature=0.5, max_tokens=32):
    #logging.info(f"autopy_test_judge: comments = `{comments}`, prototype = `{prototype}`")

    prompt, stop_strs = ask_python_test_judge(commented_code, function_name, test_code)

    logging.info(f"autopy_test_judge: prompt = \n{prompt}")
    logging.info(f"autopy_test_judge: stop_strs = {stop_strs}")

    result = ask_server(prompt, stop_strs, node, port, temperature, max_tokens)

    logging.info(f"autopy_test_judge: result = \n{result}")

    return find_first_number_between_0_and_1(result)
