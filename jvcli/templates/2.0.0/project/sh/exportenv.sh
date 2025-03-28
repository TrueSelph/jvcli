#!/bin/bash

# Export env vars
set -o allexport
if [ -f ./.env ]; then
    source ./.env
else
    echo ".env file not found"
    exit 1
fi
set +o allexport
printenv