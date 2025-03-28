#!/bin/bash
# Script to authenticate and initialize jivas agents

# Export env vars
source ./sh/exportenv.sh

# Init the user token
source ./sh/inituser.sh

# Check if JIVAS_TOKEN is set
if [ -n "$JIVAS_TOKEN" ]; then

    echo -e "\n\Initializing agents...\n"

    # Initialize agents and capture the response
    response=$(curl --silent --show-error --no-progress-meter \
    --request POST \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -H "Authorization: Bearer $JIVAS_TOKEN" \
    --data '{"reporting":"true"}' \
    "http://localhost:$JIVAS_PORT/walker/init_agents")

    # Parse the response to extract the list of "id"s without using jq
    ids=$(echo "$response" | grep -o '"id":"[^"]*"' | sed -e 's/"id":"//g' -e 's/"//g')

    # Output the list of "id"s
    echo "Initialized Agents:"
    echo "$ids \n"

else
    echo "Failed to initialize user token. Exiting..."
    exit 1
fi