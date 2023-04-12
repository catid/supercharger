#!/bin/bash

if [ -f ~/.zshrc ]; then
  . ~/.zshrc
elif [ -f ~/.bashrc ]; then
  . ~/.bashrc
fi

conda activate supercharger

git pull
pip install -r ../requirements.txt

# Check if a port argument is provided
if [ -z "$1" ]; then
    # Start the server on the default port
    python server.py
else
    # Start the server on the specified port
    python server.py --listen "$1"
fi
