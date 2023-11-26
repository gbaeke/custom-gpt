# custom-gpt

Custom GPT to query baeke.info

See this blog post: https://blog.baeke.info/?p=4178

## Modify .env

Add your Azure OpenAI API key and the Azure AI Search API key.

Generate and add the API key to protect this API.

## Modify app.py

Ensure the URLs to your Azure OpenAI instance and Azure AI Search instance are correct.

Set the correct index name.

## Build the container

Ensure deploy.sh is executable with `chmod +x deploy.sh`

Ensure Docker is installed.

Run `./deploy.sh build`

## Run the container locally

Run `./deploy.sh run`. Now test the POST request to http://localhost:8000/generate_request. Use the apicall.http file but modify it with the correct API key you set in .env

## Deploy to Azure Container Apps

Run  `./deploy.sh up`. This requires the Azure CLI on your machine. You should be logged in to your subscription with `az login`.