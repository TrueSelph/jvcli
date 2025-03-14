#!/bin/bash
# Script to create jivas user, login, and initialize jivas graph

function initialize() {

    if lsof -i :$JIVAS_PORT >/dev/null; then
        # Try to login first
        JIVAS_TOKEN=$(curl --silent --show-error --no-progress-meter \
        --request POST \
        --header 'Content-Type: application/json' \
        --header 'Accept: application/json' \
        --data '{"password": "'"$JIVAS_PASSWORD"'","email": "'"$JIVAS_USER"'"}' \
        "http://localhost:$JIVAS_PORT/user/login" | grep -o '"token":"[^"]*' | sed 's/"token":"//')

        echo $JIVAS_TOKEN

        # Check if login was successful
        if [ -z "$JIVAS_TOKEN" ] || [ "$JIVAS_TOKEN" == "null" ]; then
            echo "Login failed. Registering user..."

            # Register user if login failed
            curl --silent --show-error --no-progress-meter \
            --request POST \
            --header 'Content-Type: application/json' \
            --header 'Accept: application/json' \
            --data '{
            "password": "'"$JIVAS_PASSWORD"'",
            "email": "'"$JIVAS_USER"'"
            }' \
            "http://localhost:$JIVAS_PORT/user/register"

            # Attempt to login again after registration
            JIVAS_TOKEN=$(curl --silent --show-error --no-progress-meter \
            --request POST \
            --header 'Content-Type: application/json' \
            --header 'Accept: application/json' \
            --data '{"password": "'"$JIVAS_PASSWORD"'","email": "'"$JIVAS_USER"'"}' \
            "http://localhost:$JIVAS_PORT/user/login" | grep -oP '(?<="token":")[^"]*')
        fi

        # Print token
        echo "Jivas token: $JIVAS_TOKEN"

        echo -e "\n\nImporting demo agent...\n"
        # Import the agent
        AGENT_ID=$(curl --silent --show-error --no-progress-meter \
        --request POST \
        --header 'Content-Type: application/json' \
        --header 'Accept: application/json' \
        --header "Authorization: Bearer $JIVAS_TOKEN" \
        --data '{"daf_name": "jivas/eldon_ai"}' \
        "http://localhost:$JIVAS_PORT/walker/import_agent" | grep -o '"id":"[^"]*' | sed 's/"id":"//')

        echo "$AGENT_ID\n"
    else
        echo "Server is not running on port $JIVAS_PORT. Waiting..."
    fi

    exit
}

# Main loop to check if a process is running on port $JIVAS_PORT
while true; do
    initialize
    sleep 2  # Wait for 2 seconds before checking again
done
