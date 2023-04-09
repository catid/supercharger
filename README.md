# supercharger

Leverage locally-hosted Large Language Models to write software + unit tests for you.

Scripts are designed to run the Baize-30B model with 8-bit quantization on a cluster of multiple Linux servers each with two 3090 or 4090 GPUs using model parallelism.

Interesting features:

* Prompt engineering specifically for code, test, and evaluation.
* Generates multiple code and unit tests for a given function signature, and tries any combination of them until one code+test pair passes.
* Uses an AI to score the code and tests to decide if they are good enough and to break ties.
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

## Run an worker server

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

Results will be summarized on the console as they come in, and you can review the generated code under `./sources/`

The codegen script will stop when a generated function passes a generated unit test, and an evaluator oracle deems that the quality of the code is sufficient to stop.


## Future work

Some ideas for ways to take this further:

* Fine-tune the temperature, context-length, and max-tokens parameters to improve success rate.
* Check if we can use smaller, faster models to improve code generation speed.
* Use OpenAI API for some of the tasks in a hybrid of free + paid models.
