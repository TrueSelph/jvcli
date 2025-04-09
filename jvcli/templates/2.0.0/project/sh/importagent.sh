#!/bin/bash
# Script to create jivas user, login, and initialize jivas graph

# Check if DAF_NAME is passed as a parameter
if [ -z "$1" ]; then
    echo "Usage: $0 <DAF_NAME>"
    exit 1
fi

DAF_NAME="$1"

# Export env vars
source ./sh/exportenv.sh

# Init the user token
source ./sh/inituser.sh

# Wait until JIVAS_TOKEN is set
while [ -z "$JIVAS_TOKEN" ]; do
    echo "Waiting for JIVAS_TOKEN to be initialized..."
    sleep 1
    source ./sh/inituser.sh
done

# Check if JIVAS_TOKEN is set
if [ -n "$JIVAS_TOKEN" ]; then

    echo -e "\n\nImporting agent...\n"
    # Import the agent
    AGENT_ID=$(curl --silent --show-error --no-progress-meter \
    --request POST \
    --header 'Content-Type: application/json' \
    --header 'Accept: application/json' \
    --header "Authorization: Bearer $JIVAS_TOKEN" \
    --data "{\"daf_name\": \"$DAF_NAME\"}" \
    "http://localhost:$JIVAS_PORT/walker/import_agent" | grep -o '"id":"[^"]*' | sed 's/"id":"//')

    if [ -z "$AGENT_ID" ]; then
        echo "Failed to import agent. Exiting..."
        exit 1
    fi

    echo -e "Agent ID: $AGENT_ID\n"
else
    echo "Failed to initialize user token. Exiting..."
    exit 1
fi
