#!/bin/bash

# Change to the supercharger directory
cd "$(dirname "$0")"

python codegen/test_runner.py
