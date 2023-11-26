#!/bin/bash

# Load environment variables from .env file
export $(grep -v '^#' .env | xargs)

# Check the command line argument
if [ "$1" == "build" ]; then
    # Build the Docker image
    docker build -t myblog .
elif [ "$1" == "run" ]; then
    # Run the Docker container, mapping port 8000 to 8000 and setting environment variables
    docker run -p 8000:8000 -e OPENAI_API_KEY=$OPENAI_API_KEY -e SEARCH_KEY=$SEARCH_KEY -e API_KEY=$API_KEY myblog
elif [ "$1" == "up" ]; then
    az containerapp up -n myblog --ingress external --target-port 8000 \
        --env-vars OPENAI_API_KEY=$OPENAI_API_KEY SEARCH_KEY=$SEARCH_KEY API_KEY=$API_KEY \
        --source .
else
    echo "Usage: $0 {build|run|up}"
fi