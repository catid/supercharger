# supercharger

Leverage locally-hosted Large Language Models to write software + unit tests for you.

Scripts are designed to run the Baize-30B model with 8-bit quantization on a cluster of multiple Linux servers each with two 3090 or 4090 GPUs using model parallelism.

There is a blog post accompanying this repo: https://catid.io/posts/auto_codegen/

Interesting features:

* Prompt engineering specifically for code, test, and evaluation.
* Generates multiple code and unit tests for a given function signature, and tries any combination of them until one code+test pair passes its own tests.
* Uses an AI to score the code and tests to decide if they are good enough.
* Unit tested thorough code cleaning to remove unwanted artifacts from the model output.
* Executes the candidate code tests in a virtual machine to ensure it is safe.
* Uses a load balancer to distribute work across multiple worker nodes.


## Setup the environment

Set up docker:

```bash
sudo apt install docker.io
sudo usermod -aG docker $USER

# Log out and back in here

# Verify this command succeeds
docker info
```

Set up this repo:

```bash
git clone https://github.com/catid/supercharger
cd ./supercharger/

conda create -n supercharger python=3.10
conda activate supercharger

# Update code and packages
./update.sh

# Check to make sure everything works.  If these fail probably you need to reboot or something.
./test_code_clean.sh
./test_model.sh
```

## Run a worker server

```bash
conda activate supercharger

# Update code and packages
./update.sh

# Run the server
./run_server.sh
```

## Test the worker server

```bash
conda activate supercharger

# Test a query on the server
./test_client.sh
```


## Launch all servers in cluster from one shell command

```bash
conda activate supercharger

./launch_cluster.sh
```

The repo must be in the same place on all the machines, relative to ~.

This will read `load_balancer_nodes.txt` and launch a server process on each node.
As a pre-requisite, you'll want to first install and test the server on each node.
And you'll need to have passwordless ssh access to each node with e.g. `ssh-copy-id`.


## Run a load balancer

If you have multiple worker computers you can run a load balancer on any node.

First edit the `load_balancer_nodes.txt` file to provide node hostnames.

```bash
conda activate supercharger

./load_balancer.sh
```

When running a client, specify the load balancer port 8000 instead of 5000 to use the whole cluster.


## Test codegen

If you have one worker node:

```bash
python codegen/codegen.py --workers 1 --node localhost --port 5000
```

If you are using the load balancer on localhost:

```bash
python codegen/codegen.py
```

Results will be summarized on the console as they come in, and you can review the generated code under `./sources/func_name/`.

The codegen script will stop when a generated function passes a generated unit test, and an evaluator oracle deems that the quality of the code is sufficient to stop (you can set the threshold higher or lower with --threshold).

Example output:

```bash
(supercharger) ➜  supercharger git:(main) ✗ python codegen/codegen.py
INFO:root:Input comments: # A function that calculates the factorial of a given non-negative integer
INFO:root:Function prototype: def factorial(n):
INFO:root:Function name: factorial
INFO:root:Setting up VM...
INFO:root:Starting LLM workers...
Deleted sources/factorial/test_factorial_0.py
INFO:root:Work queue empty and detected only 0/4 workers active.  Adding job...
INFO:root:Adding a job to write more tests (tests asked/completed=0/0, codes asked/completed=0/0)
INFO:root:Worker idle... (2 seconds)
INFO:root:Worker idle... (2 seconds)
INFO:root:Worker idle... (2 seconds)
INFO:root:Work queue empty and detected only 1/4 workers active.  Adding job...
INFO:root:Adding a job to write more code (tests asked/completed=0/0, codes asked/completed=1/0)
INFO:root:Work queue empty and detected only 2/4 workers active.  Adding job...
INFO:root:Adding a job to write more tests (tests asked/completed=1/0, codes asked/completed=1/0)
INFO:root:Worker idle... (2 seconds)
INFO:root:Work queue empty and detected only 3/4 workers active.  Adding job...
INFO:root:Adding a job to write more code (tests asked/completed=1/0, codes asked/completed=2/0)
INFO:root:Work queue depth = 0 active workers = 4/4
...
INFO:root:Work queue depth = 0 active workers = 4/4
INFO:root:Generated code len=187 in 22.965782165527344 seconds, with score 0.9 (scored in 1.946894884109497 seconds)
Task ID 1: Generated code (improved=False) with score 0.9 and len=187
INFO:root:Adding a job to improve the code with self-reflection
INFO:root:Work queue depth = 1 active workers = 3/4
...
INFO:root:Work queue depth = 0 active workers = 4/4
INFO:root:Generated test len=246 in 28.84612274169922 seconds
Task ID 2: Generated test (improved=False) len=246
INFO:root:Test passed: code 1 <-> test 2 - Asking judge if we are done
INFO:root:Adding a job to improve the test with self-reflection
INFO:root:Work queue depth = 2 active workers = 3/4
INFO:root:Generated test len=307 in 32.69654178619385 seconds
Task ID 0: Generated test (improved=False) len=307
INFO:root:Test passed: code 1 <-> test 0 - Asking judge if we are done
INFO:root:Adding a job to improve the test with self-reflection
INFO:root:Work queue depth = 2 active workers = 4/4
...
INFO:root:Work queue depth = 2 active workers = 4/4
INFO:root:Generated code len=168 in 68.91890406608582 seconds, with score 0.9 (scored in 1.9692518711090088 seconds)
Task ID 3: Generated code (improved=False) with score 0.9 and len=168
INFO:root:Test passed: code 3 <-> test 2 - Asking judge if we are done
INFO:root:Test passed: code 3 <-> test 0 - Asking judge if we are done
INFO:root:Adding a job to improve the code with self-reflection
INFO:root:Work queue depth = 4 active workers = 4/4
INFO:root:Judged code/test pair with score 1.0 in 42.62114644050598 seconds
Task 5 complete: Judged pair code=1 test=2 with score=1.0
INFO:root:Work queue depth = 3 active workers = 4/4
INFO:root:Found a good code/test pair: code=1 test=2 score=1.0
INFO:root:Wrote final code and test to disk. Exiting...
```

## The results

```python
# A function that calculates the factorial of a given non-negative integer
def factorial(n: int) -> int:
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result
```

```python
import pytest
from factorial import factorial
def test_factorial():
    assert factorial(1) == 1
    assert factorial(2) == 2
    assert factorial(3) == 6
    assert factorial(4) == 24
    assert factorial(5) == 120
    assert factorial(6) == 720
```

When asked "What's your opinion of this code and unit test?", GPT-4 has this to say about the code:

```
The code implementation for the factorial function is good. It's an iterative approach, which can be more efficient in terms of memory usage compared to the recursive version. It's also more suitable for larger inputs as it does not have the risk of reaching the recursion limit.

Regarding the unit test, it is also good but has some room for improvement:

Add a test case for the base case (0), which is missing in the current test cases. The factorial of 0 is defined to be 1.
Add a test case for negative numbers to ensure the function behaves correctly with invalid input. The current implementation does not handle negative numbers, and ideally, it should raise an error in such cases.
Add more test cases for larger numbers to ensure the function works correctly for a wider range of input values.
With these improvements, the test cases would be more comprehensive and cover a wider range of scenarios.
```


## Future work

I ran out of time to implement everything I had in mind, but here are some ideas for future work:

* Check the output for cycles.
* Add a planning module that breaks up a problem into several functions and generates code for each function.
* Read the output of unit testing and use it to refine the code/tests.
* Fine-tune the temperature, context-length, and max-tokens parameters to improve success rate.
* Check if we can use smaller, faster models to improve code generation speed.
* Use OpenAI API for some of the tasks in a hybrid of free + paid models.
