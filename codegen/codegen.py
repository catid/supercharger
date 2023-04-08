import re
import os
import multiprocessing
import logging

from auto_pyfunc import auto_pyfunc
from auto_pytest import auto_pytest
from docker_execute import DockerExecute

logging.basicConfig(level=logging.INFO)

sources_dirname = "sources"
comments = "# A function that tests if a number is prime."
prototype = "def is_prime(n)"

def extract_function_name(function_def):
    # Split the function definition by whitespace
    words = re.split(r'[^A-Za-z0-9_]|(?<![A-Za-z_])[0-9]+', function_def)

    # Look for the "def" keyword and extract the function name
    for i, word in enumerate(words):
        if word == "def":
            function_name = words[i+1]
            # Strip any trailing parentheses or whitespace
            function_name = function_name.rstrip("() ")
            return function_name

    raise Exception("No function name found")

function_name = extract_function_name(prototype)

def get_script_name_from_function_name(function_name, is_test=False, variation=0):
    if is_test:
        return f"test_{function_name}_{variation}.py"
    else:
        return f"{function_name}_{variation}.py"

def write_script_to_disk(script_string, sources_dirname, func_name, is_test=False, variation=0):
    # Create the directory if it doesn't exist
    dir_path = os.path.join(sources_dirname, func_name)
    os.makedirs(dir_path, exist_ok=True)

    # Write the script to the file
    file_path = os.path.join(dir_path, get_script_name_from_function_name(func_name, is_test, variation))
    with open(file_path, "w") as f:
        f.write(script_string)

successes = 0
tries = 0

executor = DockerExecute(sources_dirname=sources_dirname)

def generate_and_write_function(function_name, sources_dirname, comments, prototype, node="localhost", port=5000, temperature=1.0, max_tokens=1024, variation=0):
    logging.info("Generating a candidate function...")
    code = auto_pyfunc(comments, prototype, node=node, port=port, temperature=temperature, max_tokens=max_tokens)

    logging.debug(f"Candidate code:\n{code}\n")
    write_script_to_disk(code, sources_dirname, function_name, is_test=False, variation=variation)

def generate_pytest_script(comments, sources_dirname, function_name, prototype, node="localhost", port=5000, temperature=1.0, max_tokens=1024, variation=0):
    logging.info("Generating a candidate pytest script...")
    test_code = auto_pytest(comments, sources_dirname, function_name, prototype, node=node, port=port, temperature=temperature, max_tokens=max_tokens)

    logging.debug(f"Test code:\n{test_code}\n")
    write_script_to_disk(test_code, sources_dirname, function_name, is_test=True, variation=variation)

node = "localhost"
port = 8000
temperature = 1.0
max_tokens = 1024

while True:
    tries += 1

    # Generate code and test in parallel

    variation = 0

    for i in range(2):
        code_process = multiprocessing.Process(target=generate_and_write_function, args=(function_name, sources_dirname, comments, prototype, node, port, temperature, max_tokens, variation))
        code_process.start()
        variation += 1

    test_variation = 0

    for i in range(2):
        test_process = multiprocessing.Process(target=generate_pytest_script, args=(comments, sources_dirname, function_name, prototype, node, port, temperature, max_tokens, variation))
        test_process.start()
        test_variation += 1

    code_process.join()
    test_process.join()

    break

    code_script_name = get_script_name_from_function_name(function_name, is_test=False, variation=variation)
    test_script_name = get_script_name_from_function_name(function_name, is_test=True, variation=variation)

    command = f"pytest {test_script_name}"
    exit_code, logs = executor.execute(script_filename=test_script_name, command=command)

    if exit_code == 0:
        successes += 1
        logging.info(f"Tests passed: {successes}/{tries} (success rate = {successes*100.0/tries}%)")
    else:
        logging.info(f"Tests failed: {successes}/{tries} (success rate = {successes*100.0/tries}%)")
