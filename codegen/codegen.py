import glob
import re
import os
import logging
import argparse
import shutil
import subprocess
from queue import Empty

from codegen_workers import JobManager
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

def get_script_name_from_function_name(function_name, is_test=False, variation=None):
    if variation is None:
        if is_test:
            return f"test_{function_name}.py"
        else:
            return f"{function_name}.py"
    else:
        if is_test:
            return f"test_{function_name}_{variation}.py"
        else:
            return f"{function_name}_{variation}.py"

def delete_old_scripts(sources_dirname, func_name):
    dir_path = os.path.join(sources_dirname, func_name)
    if os.path.exists(dir_path) and os.path.isdir(dir_path):
        py_files = glob.glob(os.path.join(dir_path, "*.py"))

        # Iterate through the list of .py files and delete them
        for py_file in py_files:
            try:
                os.remove(py_file)
                print(f"Deleted {py_file}")
            except OSError as e:
                print(f"Error deleting {py_file}: {e}")

def write_script_to_disk(code, sources_dirname, func_name, is_test=False, variation=0):
    # Create the directory if it doesn't exist
    dir_path = os.path.join(sources_dirname, func_name)
    os.makedirs(dir_path, exist_ok=True)

    # Write the script to the file
    file_path = os.path.join(dir_path, get_script_name_from_function_name(func_name, is_test, variation))
    with open(file_path, "w") as f:
        f.write(code)

def copy_candidate_scripts(source_dir, function_name, code_id, test_id):
    code_source_path = os.path.join(source_dir, function_name, get_script_name_from_function_name(function_name, is_test=False, variation=code_id))
    code_dest_path = os.path.join(source_dir, function_name, get_script_name_from_function_name(function_name, is_test=False))

    test_source_path = os.path.join(source_dir, function_name, get_script_name_from_function_name(function_name, is_test=True, variation=test_id))
    test_dest_path = os.path.join(source_dir, function_name, get_script_name_from_function_name(function_name, is_test=True))

    # Copy files
    shutil.copyfile(code_source_path, code_dest_path)
    shutil.copyfile(test_source_path, test_dest_path)

def copy_and_run_pytest(source_dir, function_name, code_id, test_id, executor):
    copy_candidate_scripts(source_dir, function_name, code_id, test_id)

    # Run pytest command
    test_script_name = os.path.join(function_name, get_script_name_from_function_name(function_name, is_test=True))
    command = f"pytest {test_script_name}"
    exit_code, logs = executor.execute(script_filename=test_script_name, command=command, timeout=10)

    return exit_code, logs

def generate_requirements(project_path, output_file='requirements.txt'):
    result = subprocess.run(['pipreqs', project_path, '--force', '--savepath', output_file], capture_output=True, text=True)
    
    if result.returncode == 0:
        return True
    else:
        logging.info(f"An error occurred while generating requirements.txt: {result}")
        return False

def install_container_requirements(sources_dirname, function_name, docker_execute):
    #logging.info("Installing container requirements.txt...")

    project_path = os.path.join(sources_dirname, function_name)
    success = generate_requirements(project_path, output_file=os.path.join(project_path, f"requirements.txt"))

    if success:
        exit_code, logs = docker_execute.execute(command=f"pip install -r {function_name}/requirements.txt")
        if exit_code != 0:
            logging.info(f"An error occurred while installing requirements.txt: exit_code={exit_code} logs={logs}")

def count_non_empty_strings(array):
    count = 0
    for item in array:
        if item is not None and isinstance(item, str) and len(item) > 0:
            count += 1
    return count

class CodeGen:
    def __init__(self, args):
        self.args = args
        self.contents = {} # dictionary: maps task_id to contents (mix of tests and codes)
        self.code_scores = {} # dictionary: maps task_id to scores (mix of tests and codes)
        self.tests = []
        self.codes = []
        self.pair_scores = {} # dictionary: maps task_id to (code_id, test_id, score)
        self.total_codes_requested = 0
        self.total_tests_requested = 0

        logging.info("Setting up VM...")

        self.docker_execute = DockerExecute(sources_dirname=args.sources_dirname)

        logging.info("Starting LLM workers...")

        self.manager = JobManager(args)

    def add_code_or_test_job(self):
        test_count = len(self.tests)
        code_count = len(self.codes)

        add_code = True

        if test_count == 0 and code_count == 0:
            add_code = self.total_tests_requested > self.total_codes_requested
        else:
            add_code = test_count > code_count

        if add_code:
            logging.info(f"Adding a job to write more code (tests asked/completed={self.total_codes_requested}/{test_count}, codes asked/completed={self.total_tests_requested}/{code_count})")
            self.manager.add_code_job()
            self.total_codes_requested += 1
        else:
            logging.info(f"Adding a job to write more tests (tests asked/completed={self.total_codes_requested}/{test_count}, codes asked/completed={self.total_tests_requested}/{code_count})")
            self.manager.add_test_job()
            self.total_tests_requested += 1

    def handle_code(self, code_id, code, score, improved=False):
        print(f"Task ID {code_id}: Generated code (improved={improved}) with score {score} and len={len(code)}")
        #print("Code:", code)

        self.codes.append(code_id)
        self.contents[code_id] = code
        self.code_scores[code_id] = score

        write_script_to_disk(
            code,
            args.sources_dirname,
            args.function_name,
            is_test=False,
            variation=code_id)

        install_container_requirements(
            args.sources_dirname,
            args.function_name,
            self.docker_execute)

        for test_id in self.tests:
            exit_code, logs = copy_and_run_pytest(
                args.sources_dirname,
                args.function_name,
                code_id,
                test_id,
                self.docker_execute)

            if exit_code != 0:
                logging.info(f"Test failed: code {code_id} <-> test {test_id}")

                if len(logs) == "":
                    logging.info("Test failed really badly somehow. Deleting {code_id} and {test_id} to avoid repeating this error.")
                    self.codes.remove(code_id)
                    self.tests.remove(test_id)
                continue

            logging.info(f"Test passed: code {code_id} <-> test {test_id} - Asking judge if we are done")

            test = self.contents[test_id]
            judge_id = self.manager.add_judge_pair_job(code, test)
            self.pair_scores[judge_id] = (code_id, test_id, None)

        if not improved:
            logging.info("Adding a job to improve the code with self-reflection")
            self.manager.add_improve_code_job(code)

    def handle_test(self, test_id, test, improved=False):
        print(f"Task ID {test_id}: Generated test (improved={improved}) len={len(test)}")
        #print("Test:", test)

        self.tests.append(test_id)
        self.contents[test_id] = test

        write_script_to_disk(
            test,
            args.sources_dirname,
            args.function_name,
            is_test=True,
            variation=test_id)

        install_container_requirements(
            args.sources_dirname,
            args.function_name,
            self.docker_execute)

        for code_id in self.codes:
            exit_code, logs = copy_and_run_pytest(
                args.sources_dirname,
                args.function_name,
                code_id,
                test_id,
                self.docker_execute)

            if exit_code != 0:
                logging.info(f"Test failed: code {code_id} <-> test {test_id}")
                continue

            logging.info(f"Test passed: code {code_id} <-> test {test_id} - Asking judge if we are done")

            code = self.contents[code_id]
            judge_id = self.manager.add_judge_pair_job(code, test)
            self.pair_scores[judge_id] = (code_id, test_id, None)

        if not improved:
            logging.info("Adding a job to improve the test with self-reflection")
            self.manager.add_improve_test_job(test)

    def handle_judge_pair(self, task_id, score):
        (code_id, test_id, _) = self.pair_scores.get(task_id)

        print(f"Task {task_id} complete: Judged pair code={code_id} test={test_id} with score={score}")

        self.pair_scores[task_id] = (code_id, test_id, score)

    def handle_results(self):
        results = self.manager.get_results(timeout=1.0)

        for result in results:
            task_op, task_id, score, data = result

            # Process a result
            if task_op == "code":
                self.handle_code(code_id=task_id, code=data, score=score, improved=False)

            elif task_op == "test":
                self.handle_test(test_id=task_id, test=data, improved=False)

            elif task_op == "improve_code":
                self.handle_code(code_id=task_id, code=data, score=score, improved=True)

            elif task_op == "improve_test":
                self.handle_test(test_id=task_id, test=data, improved=True)

            elif task_op == "judge_pair":
                self.handle_judge_pair(task_id=task_id, score=score)

    def write_code(self):
        # Delete any existing code from a previous run
        delete_old_scripts(args.sources_dirname, args.function_name)

        try:
            while True:
                self.handle_results()

                active_workers = self.manager.active_workers()
                approx_queue_depth = self.manager.approx_queue_depth()
                if approx_queue_depth == 0 and active_workers < args.workers:
                    logging.info(f"Work queue empty and detected only {active_workers}/{args.workers} workers active.  Adding job...")
                    self.add_code_or_test_job()
                else:
                    logging.info(f"Work queue depth = {approx_queue_depth} active workers = {active_workers}/{args.workers}")

                for pair_score in self.pair_scores.values():
                    (code_id, test_id, score) = pair_score
                    if score is None:
                        continue

                    if score > args.threshold:
                        logging.info(f"Found a good code/test pair: code={code_id} test={test_id} score={score}")
                        copy_candidate_scripts(args.sources_dirname, args.function_name, code_id, test_id)
                        logging.info("Wrote final code and test to disk. Exiting...")
                        return
        except KeyboardInterrupt:
            logging.info("Terminating early on user request...")
        except Exception as e:
            logging.error(f"Exception in run_queue: {e}")
        finally:
            self.manager.terminate()

def main(args):
    logging.info(f"Input comments: {args.comments}")
    logging.info(f"Function prototype: {args.prototype}")
    logging.info(f"Function name: {args.function_name}")

    codegen = CodeGen(args)
    codegen.write_code()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automatically generate Python functions and their test scripts.")
    parser.add_argument("--sources-dirname", default="sources", help="Directory where the generated source files are stored.")
    parser.add_argument("--comments", default="# A function that calculates the factorial of a given non-negative integer", help="Comments describing the desired function.")
    parser.add_argument("--prototype", default="def factorial(n)", help="Prototype of the desired function.")
    parser.add_argument("--node", default="localhost", help="Hostname or IP address of the OpenAI GPT server.")
    parser.add_argument("--port", type=int, default=8000, help="Port number of the OpenAI GPT server.")
    parser.add_argument("--temperature", type=float, default=1.0, help="Temperature parameter for the OpenAI GPT server.")
    parser.add_argument("--max-tokens", type=int, default=1024, help="Maximum number of tokens in the generated code.")
    parser.add_argument("--workers", type=int, default=4, help="Number of worker machines when using a load balancer in front of a cluster of worker nodes.")
    parser.add_argument("--threshold", type=float, default=0.95, help="Minimum threshold of code correctness before stopping.")

    args = parser.parse_args()

    args.comments = comment_multiline_string(args.comments)
    args.prototype = ensure_colon_at_end(args.prototype)
    args.function_name = extract_function_name(args.prototype)

    main(args)
