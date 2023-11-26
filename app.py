from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
import httpx, os
import dotenv
import re

# Load environment variables
dotenv.load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Constants (replace with your actual values)
api_base = "https://<OPENAIINSTANCE>.openai.azure.com/"
api_key = os.getenv("OPENAI_API_KEY")
deployment_id = "gpt-35-turbo"
search_endpoint = "https://AISEARCHINSTANCE.search.windows.net"
search_key = os.getenv("SEARCH_KEY")
search_index = "INDEXNAME"
api_version = "2023-08-01-preview"

# Pydantic model for request body
class RequestBody(BaseModel):
    query: str

# Define the API key dependency
def get_api_key(api_key: str = Header(None)):
    if api_key is None or api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return api_key

# Endpoint to generate response
@app.post("/generate_response", dependencies=[Depends(get_api_key)])
async def generate_response(request_body: RequestBody):
    url = f"{api_base}openai/deployments/{deployment_id}/extensions/chat/completions?api-version={api_version}"
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }
    data = {
        "dataSources": [
            {
                "type": "AzureCognitiveSearch",
                "parameters": {
                    "endpoint": search_endpoint,
                    "key": search_key,
                    "indexName": search_index
                }
            }
        ],
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant"
            },
            {
                "role": "user",
                "content": request_body.query
            }
        ]
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data, headers=headers, timeout=60)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    response_json = response.json()

    # get the assistant response
    assistant_content = response_json['choices'][0]['message']['content']
    assistant_content = re.sub(r'\[doc.\]', '', assistant_content)
    
    # return assistant_content as json
    return {
        "response": assistant_content
    }

# Run the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, timeout_keep_alive=60)
