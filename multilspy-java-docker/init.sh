#!/bin/bash

# Activate the virtual environment
source .env/bin/activate

echo "---- Permissions ----"

ls -la /mnt/

ls -la /mnt/repo

ls -la /mnt/input

echo "---- Code ----"


# Run the Python script with all passed arguments
python lsp-test.py "$@"