#!/bin/bash

# Change to the supercharger directory
cd "$(dirname "$0")"

conda activate supercharger

source ../update.sh

# Check if a port argument is provided
if [ -z "$1" ]; then
    # Start the server on the default port
    python server.py
else
    # Start the server on the specified port
    python server.py --listen "$1"
fi
