#!/bin/bash

# Change to the supercharger directory
cd "$(dirname "$0")"

# Start the server with default ports
python server/launch_cluster.py
