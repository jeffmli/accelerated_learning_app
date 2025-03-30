from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from backend import openai_backend_service
import mochi_backend_service
from pydantic import BaseModel
import json
from typing import Optional
from fastapi.staticfiles import StaticFiles
import os
from fastapi.responses import FileResponse
import logging

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# Models for request validation
class FlashcardRequest(BaseModel):
    deck_id: str
    front_content: str
    back_content: str

class DeckRequest(BaseModel):
    name: str
    parent_id: Optional[str] = None
    sort: Optional[int] = None
    archived: Optional[bool] = None
    trashed: Optional[str] = None
    show_sides: Optional[bool] = None
    sort_by_direction: Optional[bool] = None
    review_reverse: Optional[bool] = None
    sort_by: Optional[str] = None
    cards_view: Optional[str] = None

@app.post("/api/backend/openai")
async def openai_endpoint(request: Request):
    try:
        # Get the request body
        body = await request.json()
        logger.info(f"Received request: {body}")
        
        # Call the OpenAI service function
        response = openai_backend_service.process_request(body)
        logger.info(f"Sending response: {response}")
        return response
    except Exception as e:
        logger.error(f"Error in openai_endpoint: {str(e)}", exc_info=True)
        raise

@app.get("/api/backend/mochi/test")
async def test_mochi():
    result = mochi_backend_service.test_mochi_connection()
    return result

@app.post("/api/backend/mochi/create_card")
async def create_mochi_card(card_request: FlashcardRequest):
    result = mochi_backend_service.create_flashcard(
        card_request.deck_id,
        card_request.front_content,
        card_request.back_content
    )
    return result

@app.post("/api/backend/mochi/create_deck")
async def create_mochi_deck(deck_request: DeckRequest):
    result = mochi_backend_service.create_deck(
        deck_request.name,
        parent_id=deck_request.parent_id,
        sort=deck_request.sort,
        archived=deck_request.archived,
        trashed=deck_request.trashed,
        show_sides=deck_request.show_sides,
        sort_by_direction=deck_request.sort_by_direction,
        review_reverse=deck_request.review_reverse,
        sort_by=deck_request.sort_by,
        cards_view=deck_request.cards_view
    )
    return result

# If you need to integrate the existing OpenAI endpoints, you can add them here
# For example, if openai_backend_service has its own FastAPI app:
# app.mount("/api/openai", openai_backend_service.app)

# Get the directory of the current file
current_dir = os.path.dirname(os.path.abspath(__file__))
# Go up one level to the project root, then to the frontend directory
frontend_dir = os.path.join(os.path.dirname(current_dir), "frontend")

@app.get("/")
async def read_index():
    return FileResponse(os.path.join(frontend_dir, "index.html"))

@app.get("/script.js")
async def read_script():
    return FileResponse(os.path.join(frontend_dir, "script.js"))

@app.get("/api/debug")
async def debug():
    return {"status": "success", "message": "API is working"}

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)