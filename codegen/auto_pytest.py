import re
import ast
import logging

from ask_llm import ask_llm
from clean_code import clean_code, parse_code_blocks, only_defs_and_imports, add_missing_colons, fix_mismatched_delimiters

# Ask with reinforcing examples.  We should add more as we learn more about the model.
# Input must be of the form shown below.
def ask_llm_for_pytest(comments, prototype):
    messages = [
        {
            "role": "system",
            "content": "You are helpful AI assistant trained to write pytest code for Human given comments and prototype."
        },
        {
            "role": "Human",
            "content": "# Add two numbers and return their sum\ndef add_nums(x, y)"
        },
        {
            "role": "Assistant",
            "content": """```
import pytest
from mymodule import add_nums

def test_add_nums_positive():
    # Test case 1: adding two positive numbers
    result = add_nums(2, 3)
    assert result == 5

def test_add_nums_negative():
    # Test case 2: adding two negative numbers
    result = add_nums(-2, -3)
    assert result == -5

def test_add_nums_mixed():
    # Test case 3: adding a positive and a negative number
    result = add_nums(2, -3)
    assert result == -1
```"""
        },
        {
            "role": "Human",
            "content": "# A function that checks if an integer is prime\n# Returns true or false\ndef is_prime(n)"
        },
        {
            "role": "Assistant",
            "content": """```
def test_is_prime():
    assert is_prime(2) == True
    assert is_prime(3) == True
    assert is_prime(4) == False
    assert is_prime(5) == True
    assert is_prime(6) == False
    assert is_prime(7) == True
    assert is_prime(8) == False
    assert is_prime(9) == False
    assert is_prime(10) == False
```"""
        },
        {
            "role": "Human",
            "content": f"{comments}\n{prototype}"
        },
    ]

    return ask_llm(messages, temperature=0.7, max_tokens=2048)

def auto_pytest(comments, sources_dir, function_name, prototype):

    logging.debug(f"auto_pytest: comments = `{comments}`")
    logging.debug(f"auto_pytest: prototype = `{prototype}`")

    result = ask_llm_for_pytest(comments, prototype)

    logging.debug(f"LLM says:\n{result}")

    # Remove everything outside of the first ``` code block if found.
    try:
        code_block = parse_code_blocks(result)
        logging.debug(f"code_block:\n{code_block}\n")
        if len(code_block) > 0:
            result = code_block
    except Exception as e:
        logging.info(f"auto_pytest::parse_code_blocks failed due to exception: {e}")

    # Add missing colons and fix mismatched delimiters
    try:
        filtered = add_missing_colons(result)
        logging.debug(f"add_missing_colons:\n{filtered}\n")
        filtered = fix_mismatched_delimiters(filtered)
        logging.debug(f"fix_mismatched_delimiters:\n{filtered}\n")
        if len(filtered) > 0:
            result = filtered
    except Exception as e:
        logging.info(f"auto_pytest::add_missing_colons/fix_mismatched_delimiters failed due to exception: {e}")

    # Remove everything unexpected outside of functions
    try:
        filtered = only_defs_and_imports(result, func_name_to_exclude=function_name)
        logging.debug(f"filtered:\n{filtered}\n")
        if len(filtered) > 0:
            result = filtered
    except Exception as e:
        logging.info(f"auto_pytest::only_defs_and_imports failed due to exception: {e}")
        logging.info(f"filtered:\n{filtered}\n")

    result = clean_code(result)

    if len(result) > 0:
        # Prepend the function import
        result = '\n'.join([f"from {sources_dir}.{function_name} import {function_name}", "import pytest"] + result.splitlines())

    return result
