#!/bin/bash
# Script to init jivas user and grab token

# Check if required environment variables are set
if [ -z "$JIVAS_PORT" ] || [ -z "$JIVAS_PASSWORD" ] || [ -z "$JIVAS_USER" ]; then
    echo "Required environment variables (JIVAS_PORT, JIVAS_PASSWORD, JIVAS_USER) are not set. Exiting..."
    exit 1
fi

if lsof -i :$JIVAS_PORT >/dev/null || netstat -an | grep -q ":$JIVAS_PORT .*LISTEN"; then

    # Try to login first
    JIVAS_TOKEN=$(curl --silent --show-error --no-progress-meter \
    --request POST \
    --header 'Content-Type: application/json' \
    --header 'Accept: application/json' \
    --data '{"password": "'"$JIVAS_PASSWORD"'","email": "'"$JIVAS_USER"'"}' \
    "http://localhost:$JIVAS_PORT/user/login" | grep -o '"token":"[^"]*' | sed 's/"token":"//')

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
        "http://localhost:$JIVAS_PORT/user/login" | grep -o '"token":"[^"]*' | sed 's/"token":"//')
    fi

    # Print token
    echo "\n JIVAS token: $JIVAS_TOKEN"

else
    echo "Server is not running on port $JIVAS_PORT. Exiting..."
    exit 1
fi