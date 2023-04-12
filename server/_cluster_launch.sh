#!/bin/bash

# Change to the supercharger directory
cd "$(dirname "$0")/../"

if [ -f ~/.zshrc ]; then
  . ~/.zshrc
elif [ -f ~/.bashrc ]; then
  . ~/.bashrc
fi

conda activate supercharger

. ./update.sh

# Check if a port argument is provided
if [ -z "$1" ]; then
    # Start the server on the default port
    python server/server.py
else
    # Start the server on the specified port
    python server/server.py --listen "$1"
fi
