#!/bin/bash

# Change to the supercharger directory
cd "$(dirname "$0")"

# Start the server on default port
python server/server.py
