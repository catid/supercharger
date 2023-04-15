# Not functional.

So, it turns out that the available LLMs are not very good at detecting bugs in source code.

I've implemented a framework for testing them and determined that the best models have a success rate of about 10%.  This is not good enough to be useful.

# airate :: Static Code Analysis with AI

![airate logo](airate.jpg)

Use AI for static analysis of C++ code using the best performing LLM you can run at home.

Want to leverage AI to scan your codebase for bugs, but are unable to upload your files to Microsoft?  Here's the next best thing!

## Hardware Requirements

* 64GB RAM (or 32GB + a big swap file)
* 2x RTX3090 or RTX4090 GPUs

These models are huge.  Even with quantization, you'll need two RTX3090 or RTX4090 GPUs to run models large enough to correct analyze source code (30B or 65B).  Since 8-bit quantization is as small as you'd want to go with 30B models, they still require 2 GPUs, and in practice 65B models run about the same speed or faster than 30B models, so I'd recommend just using the default 65B model.  I'd recommend using Ubuntu Linux for the operating system on the server because makes everything easier.

I also tried llama.cpp for this and implemented a pretty good framework but it also is far too slow even with OpenBLAS.  Code here: https://github.com/catid/llamanal.cpp/tree/main/examples/analysis

## Can open-source LLVM models detect bugs in source code?

No:

```
LLaMa 65B (4-bit GPTQ) model: 1 false alarms in 15 good examples.  Detects 0 of 13 bugs.
Baize 30B (8-bit) model: 0 false alarms in 15 good examples.  Detects 1 of 13 bugs.
Galpaca 30B (8-bit) model: 0 false alarms in 15 good examples.  Detects 1 of 13 bugs.
Koala 13B (8-bit) model: 0 false alarms in 15 good examples.  Detects 0 of 13 bugs.
Vicuna 13B (8-bit) model: 2 false alarms in 15 good examples.  Detects 1 of 13 bugs.
Vicuna 7B (FP16) model: 1 false alarms in 15 good examples.  Detects 0 of 13 bugs.

GPT 3.5: 0 false alarms in 15 good examples.  Detects 7 of 13 bugs.
GPT 4: 0 false alarms in 15 good examples.  Detects 13 of 13 bugs.
```

## Setup the environment

Follow the instructions at the top of the [supercharger README](https://github.com/catid/supercharger/) to set up the environment, and to run a worker server.

Install additional dependencies:

```bash
conda install libclang

# Install additional requirements from airate directory
pip install -r airate/requirements.txt
```

## Test airate

First run the server (see parent folder for instructions) - This is how to change the model.

Then run the tests:

```bash
python airate/airate.py --node localhost --port 5000 airate/tests/
```

## Future Work

* Accepting pull requests for AST parsing of other languages.
