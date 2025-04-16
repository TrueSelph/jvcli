#!/bin/bash

# perform a jac_clean on the actions folder
# Navigate to the ./actions subdirectory and execute jac clean
if cd ./actions; then
    jac clean
    cd - > /dev/null
else
    echo "Failed to navigate to ./actions directory. Exiting..."
    exit 1
fi