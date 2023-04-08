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

def write_script_to_disk(script_string, sources_dirname, func_name):
    # Create the directory if it doesn't exist
    dir_path = os.path.join(sources_dirname, func_name)
    os.makedirs(dir_path, exist_ok=True)

    # Write the script to the file
    file_path = os.path.join(dir_path, f"{func_name}.py")
    with open(file_path, "w") as f:
        f.write(script_string)

def write_test_script_to_disk(script_string, sources_dirname, func_name):
    # Create the directory if it doesn't exist
    dir_path = os.path.join(sources_dirname, func_name)
    os.makedirs(dir_path, exist_ok=True)

    # Write the script to the file
    file_path = os.path.join(dir_path, f"test_{func_name}.py")
    with open(file_path, "w") as f:
        f.write(script_string)

successes = 0
tries = 0

executor = DockerExecute(sources_dirname=sources_dirname)

def generate_and_write_function(function_name, sources_dirname, comments, prototype):
    logging.info("Generating a candidate function...")
    code = auto_pyfunc(comments, prototype)

    logging.debug(f"Candidate code:\n{code}\n")
    write_script_to_disk(code, sources_dirname, function_name)

def generate_pytest_script(comments, sources_dirname, function_name, prototype):
    logging.info("Generating a candidate pytest script...")
    test_code = auto_pytest(comments, sources_dirname, function_name, prototype)

    logging.debug(f"Test code:\n{test_code}\n")
    write_test_script_to_disk(test_code, sources_dirname, function_name)

while True:
    tries += 1

    # Generate code and test in parallel

    code_process = multiprocessing.Process(target=generate_and_write_function, args=(function_name, sources_dirname, comments, prototype))
    code_process.start()

    test_process = multiprocessing.Process(target=generate_pytest_script, args=(comments, sources_dirname, function_name, prototype))
    test_process.start()

    code_process.join()
    test_process.join()

    test_script_name = os.path.join(sources_dirname, function_name, f"test_{function_name}.py")
    command = f"pytest {test_script_name}"

    exit_code, logs = executor.execute(script_filename=test_script_name, command=command)

    if exit_code == 0:
        successes += 1
        logging.info(f"Tests passed: {successes}/{tries} (success rate = {successes*100.0/tries}%)")
    else:
        logging.info(f"Tests failed: {successes}/{tries} (success rate = {successes*100.0/tries}%)")
