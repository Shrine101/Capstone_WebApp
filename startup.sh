#!/bin/bash

VENV_PATH="/home/lawrence/Desktop/simple_darts/simp_dart"

if [ -d "$VENV_PATH" ]; then
    source "$VENV_PATH/bin/activate"
    export PYTHONPATH="/home/lawrence/Desktop/simple_darts/Capstone_WebApp"

    # Print success messages
    echo "Virtual environment activated."
    echo "PYTHONPATH set to: $PYTHONPATH"

else
    echo "Error: Virtual environment not found "
    exit 1
fi
