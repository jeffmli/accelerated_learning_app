from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import backend.openai_backend_service as openai_backend_service
from pydantic import BaseModel
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("api.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# We're now handling the OpenAI API key in openai_backend_service.py
# so we don't need to set it here

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Model for request validation
class TextInputRequest(BaseModel):
    text: str

@app.post("/api/generate-flashcards")
async def generate_flashcards(input_request: TextInputRequest):
    """
    Endpoint to generate flashcards from user-provided text.
    Takes the text input and passes it to the OpenAI backend service.
    """
    try:
        logger.info(f"Received request with text: {input_request.text[:50]}...")
        
        # Create request data for the OpenAI service
        request_data = {"prompt": input_request.text}
        
        # Call the OpenAI service function
        response = openai_backend_service.process_request(request_data)
        
        logger.info(f"Successfully processed request")
        return {"status": "success", "data": response}
    
    except Exception as e:
        logger.error(f"Error in generate_flashcards endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Simple health check endpoint"""
    return {"status": "success", "message": "API is running"}

if __name__ == "__main__":
    uvicorn.run("backend.api:app", host="0.0.0.0", port=8000, reload=True)