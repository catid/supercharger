import os

from docker_execute import DockerExecute
from clean_code import clean_code

# Set up logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bad_code = """
Sure!  Here's the code you requested:

```python
import math

def add(a,     b):
    temp = {
        "a": a,
        "b": b
    }
    return a + b

def subtract(a, b
return a - b

def multiply(a, \\
             b)
    return a * b

def divide(a,
           b):
    return a / b

// Oh no the dumb AI typed something weird in here
def dostuff():
    x = 5
    y = 2

    print(f"{x} + {y} = {add(x, y)}")
    print(f"{x} - {y} = {subtract(x, y)}")
    print(f"{x} * {y} = {multiply(x, y)}")
    print(f"{x} / {y} = {divide(x, y)}")

    # Calculate the area of a circle
    radius = 3
    area = math.pi * (radius ** 2)
    print(f"The area of a circle with radius {radius} is {area:.2f}")

    # Calculate the square root of a number
    number = 49
    square_root = math.sqrt(number)
    print(f"The square root of {number} is {square_root}")

    # Find the maximum value in a list
    numbers = [34, 56, 12, 89, 23, 7, 91]
    max_number = max(numbers)
    print(f"The maximum value in the list is {max_number}")

    # Check if a number is prime
        num = 7
    is_prime = True
    for i in range(2, num):
        if num % i == 0:
                is_prime = False
            break

    if is_prime:
        print(f"{num} is a prime number")
    else:
        print(f"{num} is not a prime number")

def main():
    dostuff()

if __name__ == "__main__":
    main()

main()  # This is a comment
```

This code does a bunch of stuff enjoy!

"""




def main():
    code, success = clean_code(bad_code)

    if not success:
        print("Code cleaning failed!")
        return

    print(f"Cleaned code: {code}")

    # Add this call back into the code
    code += "\ndostuff()"

    # Test script file name to execute in the Docker container
    sources_dirname = "test_sources"
    test_script = "test_script.py"
    expected_output = """5 + 2 = 7
5 - 2 = 3
5 * 2 = 10
5 / 2 = 2.5
The area of a circle with radius 3 is 28.27
The square root of 49 is 7.0
The maximum value in the list is 91
7 is a prime number"""

    script_path = os.path.join(os.getcwd(), sources_dirname, test_script)
    os.makedirs(os.path.join(os.getcwd(), sources_dirname), exist_ok=True)

    # Write a simple test script to execute in the container
    with open(script_path, "w") as f:
        f.write(code)


    docker_execute = DockerExecute(sources_dirname=sources_dirname)

    # Prime the pump
    exit_code, output = docker_execute.execute(test_script)
    assert output == expected_output, f"Unexpected output: {output}"
    assert exit_code == 0, f"Unexpected exit code: {exit_code}"

    # Remove the test script file
    os.remove(script_path)

    print("Success!  Script now runs and prints the expected output.")

if __name__ == "__main__":
    main()
