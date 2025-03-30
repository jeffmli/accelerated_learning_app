# Import the OpenAI library for API access
import openai
# Import the OpenAI client class
from openai import OpenAI
# Import os module to access environment variables
import os
# Import time module for sleep
import time

# Import FastAPI framework components
from fastapi import FastAPI, HTTPException
# Import CORS middleware to handle cross-origin requests
from fastapi.middleware.cors import CORSMiddleware
# Import BaseModel for request/response data validation
from pydantic import BaseModel
# Import List type for type hinting
from typing import List

# Initialize the FastAPI application
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Set your OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Define the input model for notes
class NoteInput(BaseModel):
    notes: str

# Define the flashcard model structure
class Flashcard(BaseModel):
    front: str  # Question side of the flashcard
    back: str   # Answer side of the flashcard

# Define endpoint for basic flashcard generation (mock data)
@app.post("/generate-flashcards", response_model=List[Flashcard])
async def generate_flashcards(note_input: NoteInput):
    # Strip whitespace from input notes
    notes = note_input.notes.strip()
    
    # Validate that notes are not empty
    if not notes:
        raise HTTPException(status_code=400, detail="Notes cannot be empty")

    # Return mock flashcards (for testing/demo purposes)
    flashcards = [
        {"front": "What is X?", "back": "X is Y"},
        {"front": "What is A?", "back": "A is B"}
    ]

    return flashcards

# Define endpoint for OpenAI-powered flashcard generation
@app.post("/generate-flashcards-openai", response_model=List[Flashcard])
async def generate_flashcards_openai(note_input: NoteInput):
    # Strip whitespace from input notes
    notes = note_input.notes.strip()
    
    # Validate that notes are not empty
    if not notes:
        raise HTTPException(status_code=400, detail="Notes cannot be empty")
    
    # Check if the input text is too short
    if len(notes) < 50:  # Minimum character threshold
        return [Flashcard(front="Input too short", back="Add more notes to get a response.")]

    max_retries = 3
    retry_delay = 2  # seconds
    attempt = 0

    while attempt < max_retries:
        try:
            # Initialize the OpenAI client
            client = OpenAI()

            # Create the prompt for the OpenAI API
            prompt = f"""
            Generate flashcards from the following notes. 
            Each flashcard should have a question on the front and the answer on the back.
            Return the flashcards as a JSON array of objects with 'front' and 'back' fields.
            
            Notes:
            {notes}
            
            Format example:
            [
                {{"front": "What is X?", "back": "X is Y"}},
                {{"front": "What is the capital of France?", "back": "Paris"}}
            ]
            """

            # Make the API call to OpenAI
            response = client.chat.completions.create(
                model="gpt-4o",  # Specify the model to use
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates flashcards from notes."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}  # Request JSON format response
            )

            # Print the prompt for debugging
            print(prompt)

            # Extract the content from the API response
            flashcards_json = response.choices[0].message.content

            # Print the JSON response for debugging
            print(flashcards_json)
            # Import json module for parsing the response
            import json
            # Parse the JSON and extract the flashcards array
            flashcards = json.loads(flashcards_json).get("flashcards", [])
            
            # Validate each flashcard has the correct structure
            validated_flashcards = []
            for card in flashcards:
                # Check if card is a dictionary with required fields
                if isinstance(card, dict) and "front" in card and "back" in card:
                    # Create a validated Flashcard object
                    validated_flashcards.append(Flashcard(front=card["front"], back=card["back"]))
            
            # Ensure at least one valid flashcard was generated
            if not validated_flashcards:
                raise ValueError("No valid flashcards were generated")

            # Return the validated flashcards
            return validated_flashcards
        except Exception as e:
            # Log any errors that occur
            print(f"Error during OpenAI API call: {e}")
            attempt += 1
            if attempt < max_retries:
                print(f"Retrying... ({attempt}/{max_retries})")
                time.sleep(retry_delay)
            else:
                raise HTTPException(status_code=500, detail="Failed to generate flashcards after multiple attempts.") 