import requests
import json
from requests.auth import HTTPBasicAuth
import os

# Configuration
MOCHI_API_BASE_URL = "https://app.mochi.cards/api"  # Replace with actual Mochi API URL
API_KEY = os.environ.get("MOCHI_API_KEY") # Replace with your actual API key


def create_flashcard(deck_id, front_content, back_content):
    """
    Creates a flashcard in the specified Mochi deck
    
    Args:
        deck_id (str): The ID of the deck to add the card to
        front_content (str): Content for the front of the card
        back_content (str): Content for the back of the card
        
    Returns:
        dict: Response from the Mochi API
    """
    try:
        payload = {
            "deck_id": deck_id,
            "front": front_content,
            "back": back_content
        }
        
        response = requests.post(
            f"{MOCHI_API_BASE_URL}/cards",
            auth=HTTPBasicAuth(API_KEY, ''),  # Empty password
            headers={
                "Content-Type": "application/json"
            },
            data=json.dumps(payload)
        )
        
        response.raise_for_status()
        return {
            "status": "success",
            "message": "Flashcard created successfully",
            "data": response.json()
        }
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "message": f"Failed to create flashcard: {str(e)}"
        }

# Add a function to get all decks
def get_decks():
    """
    Get all decks from Mochi
    
    Returns:
        dict: Response from the Mochi API containing all decks
    """
    try:
        response = requests.get(
            f"{MOCHI_API_BASE_URL}/decks",
            auth=HTTPBasicAuth(API_KEY, ''),  # Empty password
            headers={
                "Content-Type": "application/json"
            }
        )
        
        response.raise_for_status()
        return {
            "status": "success",
            "message": "Successfully retrieved decks",
            "data": response.json()
        }
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "message": f"Failed to retrieve decks: {str(e)}"
        }

def create_deck(name, parent_id=None, sort=None, archived=None, trashed=None, 
                show_sides=None, sort_by_direction=None, review_reverse=None,
                sort_by=None, cards_view=None):
    """
    Create a new deck in Mochi with full customization options
    
    Args:
        name (str): The name of the deck
        parent_id (str, optional): ID of the parent deck
        sort (int, optional): Sort order
        archived (bool, optional): Whether the deck is archived
        trashed (str, optional): ISO timestamp when the deck was trashed
        show_sides (bool, optional): Whether to show sides
        sort_by_direction (bool, optional): Sort direction
        review_reverse (bool, optional): Whether to review in reverse
        sort_by (str, optional): How cards are sorted on the deck page
        cards_view (str, optional): How cards are displayed on the deck page
        
    Returns:
        dict: Response from the Mochi API containing the created deck
    """
    try:
        # Start with the required name field
        payload = {
            "name": name
        }
        
        # Add optional fields if they are provided
        if parent_id is not None:
            payload["parent-id"] = parent_id
        
        if sort is not None:
            payload["sort"] = sort
            
        if archived is not None:
            payload["archived?"] = archived
            
        if trashed is not None:
            payload["trashed?"] = trashed
            
        if show_sides is not None:
            payload["show-sides?"] = show_sides
            
        if sort_by_direction is not None:
            payload["sort-by-direction"] = sort_by_direction
            
        if review_reverse is not None:
            payload["review-reverse?"] = review_reverse
            
        if sort_by is not None:
            payload["sort-by"] = sort_by
            
        if cards_view is not None:
            payload["cards-view"] = cards_view
            
        # Print the payload for debugging
        print(f"Creating deck with payload: {json.dumps(payload)}")
            
        response = requests.post(
            f"{MOCHI_API_BASE_URL}/decks",
            auth=HTTPBasicAuth(API_KEY, ''),  # Empty password
            headers={
                "Content-Type": "application/json"
            },
            data=json.dumps(payload)
        )
        
        # Print the response for debugging
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        response.raise_for_status()
        return {
            "status": "success",
            "message": "Deck created successfully",
            "data": response.json()
        }
    except requests.exceptions.RequestException as e:
        error_message = str(e)
        response_text = ""
        
        # Try to get more details from the response if available
        if hasattr(e, 'response') and e.response is not None:
            try:
                response_text = e.response.text
            except:
                pass
                
        return {
            "status": "error",
            "message": f"Failed to create deck: {error_message}",
            "details": response_text
        }

# # If you want to expose this as an API endpoint using Flask
if __name__ == "__main__":
    # Simple test to run directly
    # result = test_mochi_connection()
    result = create_deck("test deck")
    print(result)
