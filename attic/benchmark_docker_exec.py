import os
import docker
import timeit
from docker_execute import DockerExecute

# Test script file name to execute in the Docker container
test_script = "test_script.py"

# Write a simple test script to execute in the container
with open(test_script, "w") as f:
    f.write("print('Hello, Docker!')")

# Set up the benchmarking function
def benchmark_docker_execute():
    docker_execute = DockerExecute()

    try:
        # Measure the execution time of the test_code method
        exec_time = timeit.timeit(
            lambda: docker_execute.test_code(test_script), number=1
        )
    finally:
        # Clean up the Docker container
        docker_execute.cleanup()

    return exec_time

# Run the benchmark
exec_time = benchmark_docker_execute()
print(f"Execution time of the test_code method: {exec_time:.6f} seconds")

# Remove the test script file
os.remove(test_script)
