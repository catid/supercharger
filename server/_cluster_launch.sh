#!/bin/bash

# Change to the supercharger directory
cd "$(dirname "$0")"

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
    python server.py & pid=$!
else
    # Start the server on the specified port
    python server.py --listen "$1" & pid=$!
fi

# Set up a signal handler to kill the program when the script ends
trap ctrl_c INT
function ctrl_c() {
    kill $pid
    exit
}

# Sleep forever
sleep infinity
