# Use modules from parent folder
import os, sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

import re

from server.client import ask_server
from prompts.ask_templates import ask_cpp_expert_score, ask_python_expert_score, ask_cs_expert_score, ask_js_expert_score, ask_java_expert_score, ask_ts_expert_score, ask_php_expert_score

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

def cpp_oracle(code, node="localhost", port=5000, temperature=0.0, max_tokens=4):
    prompt, stop_strs = ask_cpp_expert_score(code)
    result = ask_server(prompt, stop_strs, node, port, temperature, max_tokens)
    return find_first_number_between_0_and_1(result)

def py_oracle(code, node="localhost", port=5000, temperature=0.0, max_tokens=4):
    prompt, stop_strs = ask_python_expert_score(code)
    result = ask_server(prompt, stop_strs, node, port, temperature, max_tokens)
    return find_first_number_between_0_and_1(result)

def cs_oracle(code, node="localhost", port=5000, temperature=0.0, max_tokens=4):
    prompt, stop_strs = ask_cs_expert_score(code)
    result = ask_server(prompt, stop_strs, node, port, temperature, max_tokens)
    return find_first_number_between_0_and_1(result)

def js_oracle(code, node="localhost", port=5000, temperature=0.0, max_tokens=4):
    prompt, stop_strs = ask_js_expert_score(code)
    result = ask_server(prompt, stop_strs, node, port, temperature, max_tokens)
    return find_first_number_between_0_and_1(result)

def java_oracle(code, node="localhost", port=5000, temperature=0.0, max_tokens=4):
    prompt, stop_strs = ask_java_expert_score(code)
    result = ask_server(prompt, stop_strs, node, port, temperature, max_tokens)
    return find_first_number_between_0_and_1(result)

def ts_oracle(code, node="localhost", port=5000, temperature=0.0, max_tokens=4):
    prompt, stop_strs = ask_ts_expert_score(code)
    result = ask_server(prompt, stop_strs, node, port, temperature, max_tokens)
    return find_first_number_between_0_and_1(result)

def php_oracle(code, node="localhost", port=5000, temperature=0.0, max_tokens=4):
    prompt, stop_strs = ask_php_expert_score(code)
    result = ask_server(prompt, stop_strs, node, port, temperature, max_tokens)
    return find_first_number_between_0_and_1(result)
