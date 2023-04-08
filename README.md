# supercharger

Leverage locally-hosted LLMs to write software for you.

Scripts are designed to run the Baize-30B model with 8-bit quantization on a cluster of multiple Linux servers each with two 3090 or 4090 GPUs using model parallelism.  Code generation takes advantage of parallelism by writing candidate code and unit tests on separate workers.

## Setup the environment

```bash
git clone https://github.com/catid/supercharger
cd ./supercharger/

conda create -n supercharger python=3.10
conda activate supercharger

# Update code and packages
./update.sh

# Check to make sure everything works
./test_model.sh
```

## Run an inference server

```bash
conda activate supercharger

# Update code and packages
./update.sh

# Run the server
./run_server.sh
```

## Test the inference server

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

```bash
python codegen/test_codegen.py
```
