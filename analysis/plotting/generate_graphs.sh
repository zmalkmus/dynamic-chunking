#!/bin/bash

# Loop over all .py files in the current directory
for file in *.py; do
    # Check if there are any .py files in the directory
    if [ -f "$file" ]; then
        echo "Running $file"
        python "$file"
        echo "Finished running $file"
    else
        echo "No Python files found in the directory."
        break
    fi
done
