import re
import os
import multiprocessing
import logging
import argparse

from auto_pyfunc import auto_pyfunc
from auto_pytest import auto_pytest
from docker_execute import DockerExecute

logging.basicConfig(level=logging.INFO)

def comment_multiline_string(s: str) -> str:
    lines = s.split("\n")
    commented_lines = []
    for line in lines:
        stripped_line = line.lstrip()
        whitespace = line[:len(line) - len(stripped_line)]
        if stripped_line and not stripped_line.startswith("#"):
            commented_line = whitespace + "# " + stripped_line
        else:
            commented_line = line
        commented_lines.append(commented_line)
    return "\n".join(commented_lines)

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

def generate_and_write_function(function_name, sources_dirname, comments, prototype, node="localhost", port=5000, temperature=1.0, max_tokens=1024, variation=0):
    logging.info("Generating a candidate function...")
    code = auto_pyfunc(comments, prototype, node=node, port=port, temperature=temperature, max_tokens=max_tokens)

    logging.debug(f"Candidate code:\n{code}\n")
    write_script_to_disk(code, sources_dirname, function_name, is_test=False, variation=variation)

def generate_pytest_script(comments, sources_dirname, function_name, prototype, node="localhost", port=5000, temperature=1.0, max_tokens=1024, variation=0):
    logging.info("Generating a candidate pytest script...")
    test_code = auto_pytest(comments, prototype, node=node, port=port, temperature=temperature, max_tokens=max_tokens)

    logging.debug(f"Test code:\n{test_code}\n")
    write_script_to_disk(test_code, sources_dirname, function_name, is_test=True, variation=variation)

def main(args):
    comments = comment_multiline_string(args.comments)
    function_name = extract_function_name(args.prototype)

    logging.info(f"Input comments: {comments}")
    logging.info(f"Function prototype: {args.prototype}")
    logging.info(f"Function name: {function_name}")

    successes = 0
    tries = 0

    logging.info("Creating docker executor...")

    executor = DockerExecute(sources_dirname=args.sources_dirname)

    variation = 0
    test_variation = 0

    while True:
        tries += 1

        logging.info("Generating code and test...")

        # Generate code and test in parallel

        for i in range(2):
            code_process = multiprocessing.Process(target=generate_and_write_function, args=(function_name, args.sources_dirname, comments, args.prototype, args.node, args.port, args.temperature, args.max_tokens, variation))
            code_process.start()
            variation += 1

        for i in range(2):
            test_process = multiprocessing.Process(target=generate_pytest_script, args=(comments, args.sources_dirname, function_name, args.prototype, args.node, args.port, args.temperature, args.max_tokens, variation))
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automatically generate Python functions and their test scripts.")
    parser.add_argument("--sources-dirname", default="sources", help="Directory where the generated source files are stored.")
    parser.add_argument("--comments", default="# A function that tests if a number is prime.", help="Comments describing the desired function.")
    parser.add_argument("--prototype", default="def is_prime(n)", help="Prototype of the desired function.")
    parser.add_argument("--node", default="localhost", help="Hostname or IP address of the OpenAI GPT server.")
    parser.add_argument("--port", type=int, default=8000, help="Port number of the OpenAI GPT server.")
    parser.add_argument("--temperature", type=float, default=1.0, help="Temperature parameter for the OpenAI GPT server.")
    parser.add_argument("--max-tokens", type=int, default=1024, help="Maximum number of tokens in the generated code.")

    args = parser.parse_args()

    main(args)
