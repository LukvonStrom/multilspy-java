#!/bin/bash

# Activate the virtual environment
source .env/bin/activate

# Run the Python script with all passed arguments
python lsp-test.py "$@"