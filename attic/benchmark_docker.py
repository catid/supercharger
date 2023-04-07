import docker
import time

client = docker.from_env()

client.images.pull("python:3.10")

# Define the "Hello World" Python code
hello_world_code = "print('Hello, World!')"

# Measure the time taken to run the "Hello World" code within the Docker container
start_time = time.time()

# Use the Docker SDK for Python to create a container that runs the "Hello World" code
container = client.containers.create(
    "python:3.10",
    command=f'python -c "{hello_world_code}"',
    detach=True,
)

container.start()
container.wait()

end_time = time.time()
elapsed_time = end_time - start_time

# Retrieve and print the output from the container
logs = container.logs().decode("utf-8")
print("Output from the container:")
print(logs)

# Print the elapsed time
print(f"Elapsed time: {elapsed_time} seconds")

# Remove the container
container.remove()
