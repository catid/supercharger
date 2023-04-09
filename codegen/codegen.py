import re
import os
import multiprocessing
import logging
import argparse
import shutil
import subprocess

from autopy import autopy_func, autopy_func_improve, autopy_test, autopy_test_improve
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

def ensure_colon_at_end(prototype: str) -> str:
    if not prototype.endswith(':'):
        prototype += ':'
    return prototype

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

def write_script_to_disk(code, sources_dirname, func_name, is_test=False, variation=0):
    # Create the directory if it doesn't exist
    dir_path = os.path.join(sources_dirname, func_name)
    os.makedirs(dir_path, exist_ok=True)

    # Write the script to the file
    file_path = os.path.join(dir_path, get_script_name_from_function_name(func_name, is_test, variation))
    with open(file_path, "w") as f:
        f.write(code)

def copy_and_run_pytest(source_dir, function_name, variation, test_variation, executor):
    source_file = os.path.join(source_dir, function_name, f"{function_name}_{variation}.py")
    test_source_file = os.path.join(source_dir, function_name, f"test_{function_name}_{test_variation}.py")

    dest_file = os.path.join(source_dir, function_name, f"{function_name}.py")
    test_dest_file = os.path.join(source_dir, function_name, f"test_{function_name}.py")

    # Copy files
    shutil.copyfile(source_file, dest_file)
    shutil.copyfile(test_source_file, test_dest_file)

    # Run pytest command
    test_script_name = f"{function_name}/test_{function_name}.py"
    command = f"pytest {test_script_name}"
    exit_code, logs = executor.execute(script_filename=test_script_name, command=command)

    return exit_code, logs

def code_generating_worker(queue, args, write_code=True, write_test=True):
    while True:
        if write_code:
            logging.info("Generating code...")
            code = autopy_func(args.comments, args.prototype, node=args.node, port=args.port, temperature=args.temperature, max_tokens=args.max_tokens)

            if len(code) > 0:
                queue.put(("code", code))

        if write_test:
            logging.info("Generating test...")
            test = autopy_test(args.comments, args.prototype, args.function_name, node=args.node, port=args.port, temperature=args.temperature, max_tokens=args.max_tokens)

            if len(test) > 0:
                queue.put(("test", test))

        if write_code and len(code) > 0:
            logging.info("Improving code...")
            code = autopy_func_improve(args.comments, code, node=args.node, port=args.port, temperature=args.temperature, max_tokens=args.max_tokens)

            if len(code) > 0:
                queue.put(("code", code))

        if write_test and len(test) > 0:
            logging.info("Improving test...")
            test = autopy_test_improve(args.comments, args.prototype, args.function_name, test, node=args.node, port=args.port, temperature=args.temperature, max_tokens=args.max_tokens)

            if len(test) > 0:
                queue.put(("test", test))

def launch_workers(queue, args):
    workers = []

    if args.workers == 1:
        write_code = True
        write_test = True
        p = multiprocessing.Process(target=code_generating_worker, args=(queue, args, write_code, write_test))
        p.start()
        workers.append(p)
    else:
        for i in range(args.workers):
            write_code = (i % 2) == 0
            write_test = (i % 2) == 1
            p = multiprocessing.Process(target=code_generating_worker, args=(queue, args, write_code, write_test))
            p.start()
            workers.append(p)

def terminate_workers(workers):
    for worker in workers:
        worker.terminate()

def generate_requirements(project_path, output_file='requirements.txt'):
    result = subprocess.run(['pipreqs', project_path, '--force', '--savepath', output_file], capture_output=True, text=True)
    
    if result.returncode == 0:
        return True
    else:
        logging.info(f"An error occurred while generating requirements.txt: {result}")
        return False

def install_container_requirements(sources_dirname, function_name, docker_execute):
    logging.info("Installing container requirements.txt...")

    project_path = os.path.join(sources_dirname, function_name)
    success = generate_requirements(project_path, output_file=os.path.join(project_path, f"requirements.txt"))

    if success:
        exit_code, logs = docker_execute.execute(command=f"pip install -r {function_name}/requirements.txt")
        if exit_code != 0:
            logging.info(f"An error occurred while installing requirements.txt: exit_code={exit_code} logs={logs}")
        else:
            logging.info("Successfully installed container requirements.txt")


def write_code(args):
    logging.info("Setting up...")

    queue = multiprocessing.Queue()
    docker_execute = DockerExecute(sources_dirname=args.sources_dirname)

    logging.info("Starting background workers...")

    workers = launch_workers(queue, args)

    logging.info("Waiting for first result...")

    code_variation = 0
    test_variation = 0
    codes = []
    tests = []

    try:
        while True:
            (type, code) = queue.get()

            if type == "code":
                logging.info(f"Got code {code_variation}")
                codes.append(code)
                write_script_to_disk(code, args.sources_dirname, args.function_name, is_test=False, variation=code_variation)

                install_container_requirements(args.sources_dirname, args.function_name, docker_execute)

                for i, _ in enumerate(tests):
                    exit_code, logs = copy_and_run_pytest(args.sources_dirname, args.function_name, code_variation, i, docker_execute)
                    if exit_code == 0:
                        logging.info(f"Test passed: code {code_variation} <-> test {i}")
                    else:
                        logging.info(f"Test failed: code {code_variation} <-> test {i}") #: exit_code={exit_code} logs={logs}")
                    # FIXME: Use the logs to help improve things

                code_variation += 1
            elif type == "test":
                logging.info(f"Got test {test_variation}")
                tests.append(code)
                write_script_to_disk(code, args.sources_dirname, args.function_name, is_test=True, variation=test_variation)

                install_container_requirements(args.sources_dirname, args.function_name, docker_execute)

                for i, _ in enumerate(codes):
                    exit_code, logs = copy_and_run_pytest(args.sources_dirname, args.function_name, i, test_variation, docker_execute)
                    if exit_code == 0:
                        logging.info(f"Test passed: code {i} <-> test {test_variation}")
                    else:
                        logging.info(f"Test failed: code {i} <-> test {test_variation}") #: exit_code={exit_code} logs={logs}")
                    # FIXME: Use the logs to help improve things

                test_variation += 1

    except Exception as e:
        logging.error(f"Exception in run_queue: {e}")
    finally:
        terminate_workers(workers)

def main(args):
    logging.info(f"Input comments: {args.comments}")
    logging.info(f"Function prototype: {args.prototype}")
    logging.info(f"Function name: {args.function_name}")

    write_code(args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automatically generate Python functions and their test scripts.")
    parser.add_argument("--sources-dirname", default="sources", help="Directory where the generated source files are stored.")
    parser.add_argument("--comments", default="# A function that tests if a number is prime.", help="Comments describing the desired function.")
    parser.add_argument("--prototype", default="def is_prime(n)", help="Prototype of the desired function.")
    parser.add_argument("--node", default="localhost", help="Hostname or IP address of the OpenAI GPT server.")
    parser.add_argument("--port", type=int, default=8000, help="Port number of the OpenAI GPT server.")
    parser.add_argument("--temperature", type=float, default=1.0, help="Temperature parameter for the OpenAI GPT server.")
    parser.add_argument("--max-tokens", type=int, default=1024, help="Maximum number of tokens in the generated code.")
    parser.add_argument("--workers", type=int, default=4, help="Number of worker machines when using a load balancer in front of a cluster of worker nodes.")

    args = parser.parse_args()

    args.comments = comment_multiline_string(args.comments)
    args.prototype = ensure_colon_at_end(args.prototype)
    args.function_name = extract_function_name(args.prototype)

    main(args)
