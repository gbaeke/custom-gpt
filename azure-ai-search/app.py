from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
import os
from typing import List
import dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.models import VectorizedQuery
import openai
import logging

logger = logging.getLogger("uvicorn")
logger.setLevel(logging.INFO)

# Load environment variables
dotenv.load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Constants (replace with your actual values)
search_endpoint = "https://acs-geba.search.windows.net"
search_key = os.getenv("SEARCH_KEY")
search_index = "blog"
api_version = "2023-08-01-preview"

# Pydantic model for blog post
class BlogPost(BaseModel):
    title: str
    content: str
    url: str

# Pydantic model for request body
class RequestBody(BaseModel):
    query: str

# Pydantic model for response body
class ResponseBody(BaseModel):
    response: List[BlogPost]

def get_embeddings(text: str):
    import openai

    open_ai_endpoint = os.getenv("AZURE_OPENAI_EMBEDDING_ENDPOINT")
    open_ai_key = os.getenv("OPENAI_API_KEY")

    client = openai.AzureOpenAI(
        azure_endpoint=open_ai_endpoint,
        api_key=open_ai_key,
        api_version="2023-09-01-preview",
    )
    # make sure this model is deployed in your Azure OpenAI resource
    embedding = client.embeddings.create(input=[text], model="text-embedding-ada-002")
    return embedding.data[0].embedding

# Define the API key dependency
def get_api_key(api_key: str = Header(None)):
    if api_key is None or api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return api_key

# Endpoint to generate response
@app.post("/generate_response", response_model=ResponseBody, dependencies=[Depends(get_api_key)])
async def generate_response(request_body: RequestBody):
    service_endpoint = "https://acs-geba.search.windows.net"
    index_name = "blog"
    key = os.getenv("SEARCH_KEY")
    query = request_body.query

    search_client = SearchClient(service_endpoint, index_name, AzureKeyCredential(key))
    logger.info(f"Staring query: {query}")
    vector_query = VectorizedQuery(vector=get_embeddings(query), k_nearest_neighbors=5, fields="contentVector")

    results = search_client.search(
        vector_queries=[vector_query],
        select=["Content", "Title", "Url"],
        top=5
    )

    result_list = []
    for result in results:
        result_list.append(
            {
                "title": result["Title"],
                "content": result["Content"],
                "url": result["Url"],
            }
        )
    
    
    # return result_list as json
    return ResponseBody(response=result_list)

# Run the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, timeout_keep_alive=60)
