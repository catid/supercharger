import os
import timeit

from docker_execute import DockerExecute

# Test script file name to execute in the Docker container
sources_dirname = "test_sources"
test_script = "test_script.py"
expected_output = "Hello, Docker!"

script_path = os.path.join(os.getcwd(), sources_dirname, test_script)
os.makedirs(os.path.join(os.getcwd(), sources_dirname), exist_ok=True)

# Write a simple test script to execute in the container
with open(script_path, "w") as f:
    f.write(f"print('{expected_output}')\n")

# Set up the benchmarking function
def benchmark_docker_execute():
    print("Setting up...")

    docker_execute = DockerExecute(sources_dirname=sources_dirname)

    # Prime the pump
    exit_code, output = docker_execute.execute(test_script)
    assert output == expected_output, f"Unexpected output: {output}"
    assert exit_code == 0, f"Unexpected exit code: {exit_code}"

    print("Benchmarking...")

    try:
        # Measure the execution time of the method
        exec_time = timeit.timeit(
            lambda: docker_execute.execute(test_script), number=4
        )
    finally:
        # Clean up the Docker container
        docker_execute.shutdown()

    return exec_time

# Run the benchmark
exec_time = benchmark_docker_execute()
print(f"DockerExecute method: {exec_time:.6f} seconds")

# Remove the test script file
os.remove(script_path)
