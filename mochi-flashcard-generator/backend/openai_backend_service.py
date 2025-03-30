import openai
import logging
import os



logger = logging.getLogger(__name__)

openai.api_key = os.environ.get("OPENAI_API_KEY")

def generate_response(prompt: str):
    """
    Generate a response using OpenAI
    """
    try:
        # The issue is that os.environ.get() is looking for an environment variable with that name,
        # not using the string itself as the API key. Let's set it directly:

        print(openai.api_key)

        client = openai.OpenAI(api_key="Add API Key Here")

        response = client.responses.create(
            model="gpt-4o",
            input=f"{prompt}"
        )

        print(response.output_text)
        return response.output_text
    
    except Exception as e:
        print(f"OpenAI API error: {str(e)}")  # Add debug logging
        return {
            "status": "error",
            "message": str(e)
        }

def process_request(request_data):
    """
    Process a request from the API
    """
    try:
        prompt = request_data.get("prompt", "")
        logger.info(f"Processing prompt: {prompt[:50]}...")  # Log first 50 chars
        
        # Fix: Use double curly braces to escape them in f-strings
        enhanced_prompt = f"""
        Generate flashcards from the following notes. 
        Format the response as a JSON array of objects with 'front' and 'back' properties.
        Example:
        [
            {{"front": "What is the capital of France?", "back": "Paris"}},
            {{"front": "What is the largest planet in our solar system?", "back": "Jupiter"}}
        ]
        Notes: {prompt}
        """
        print(enhanced_prompt)
        
        result = generate_response(enhanced_prompt)
        return result
    except Exception as e:
        logger.error(f"Error in process_request: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "message": f"Internal server error: {str(e)}"
        }

# If you need to keep this file runnable on its own:
if __name__ == "__main__":
    request = {
        "prompt": "Hello"
    }
    result = process_request(request)

    print(result)
    
    