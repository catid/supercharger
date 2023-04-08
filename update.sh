#!/bin/bash

# Change to the supercharger directory
cd "$(dirname "$0")"

# Upgrade code and packages
git pull
pip install --upgrade -r requirements.txt
