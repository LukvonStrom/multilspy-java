#!/bin/bash

# Activate the virtual environment
source .env/bin/activate

# Print the full command
echo "Running command: timeout -k 10s 300s python cli_entrypoint.py $@"

# Run the Python script with all passed arguments
timeout -k 10s 300s python cli_entrypoint.py "$@"