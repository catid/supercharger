import ast
import logging

from ask_llm import ask_llm
from clean_code import clean_code, parse_code_blocks, find_first_function, add_missing_colons, fix_mismatched_delimiters

# Ask with reinforcing examples.  We should add more as we learn more about the model.
# Input must be of the form shown below.
def ask_llm_for_function(comments, prototype):
    messages = [
        {
            "role": "system",
            "content": "You are helpful AI assistant trained to write Python functions for Human given comments and prototype."
        },
        {
            "role": "Human",
            "content": "# Add two numbers and return their sum\ndef add_nums(x, y)"
        },
        {
            "role": "Assistant",
            "content": """```
def add_nums(x, y):
    return x + y
```"""
        },
        {
            "role": "Human",
            "content": "# Write a function that multiplies two floats\ndef mul_nums(a, b)"
        },
        {
            "role": "Assistant",
            "content": """```
def mul_nums(x: float, y: float) -> float:
    return x * y
```"""
        },
        {
            "role": "Human",
            "content": "# A function that checks if an integer is prime\n# Returns true or false\ndef is_prime(n)"
        },
        {
            "role": "Assistant",
            "content": """```
def is_prime(n: int) -> bool:
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True
```"""
        },
        {
            "role": "Human",
            "content": f"{comments}\n{prototype}"
        },
    ]

    return ask_llm(messages, temperature=0.7, max_tokens=2048)

def auto_pyfunc(comments, prototype):

    logging.debug(f"auto_pyfunc: comments = `{comments}`")
    logging.debug(f"auto_pyfunc: prototype = `{prototype}`")

    result = ask_llm_for_function(comments, prototype)

    logging.debug(f"LLM says:\n{result}")

    # Remove everything outside of the first ``` code block if found.
    try:
        code_block = parse_code_blocks(result)
        logging.debug(f"code_block:\n{code_block}\n")
        if len(code_block) > 0:
            result = code_block
    except Exception as e:
        logging.info(f"auto_pyfunc::parse_code_blocks failed due to exception: {e}")

    # Add missing colons and fix mismatched delimiters
    try:
        filtered = add_missing_colons(result)
        logging.debug(f"add_missing_colons:\n{filtered}\n")
        filtered = fix_mismatched_delimiters(filtered)
        logging.debug(f"fix_mismatched_delimiters:\n{filtered}\n")
        if len(filtered) > 0:
            result = filtered
    except Exception as e:
        logging.info(f"auto_pyfunc::add_missing_colons/fix_mismatched_delimiters failed due to exception: {e}")

    # Remove everything unexpected outside of functions
    try:
        filtered = find_first_function(result)
        logging.debug(f"find_first_function:\n{filtered}\n")
        if len(filtered) > 0:
            result = filtered
    except Exception as e:
        logging.info(f"auto_pyfunc::find_first_function failed due to exception: {e}")
        logging.info(f"find_first_function:\n{filtered}\n")

    result = clean_code(result)

    if len(result) > 0:
        # Prepend the comments
        result = '\n'.join(comments.splitlines() + result.splitlines())

    return result
