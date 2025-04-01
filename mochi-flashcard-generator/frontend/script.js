// Wait for the DOM to fully load before executing any JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Get references to the HTML elements we need to interact with
    const notesInput = document.getElementById('notes-input');           // The textarea where users input their notes
    const generateBtn = document.getElementById('generate-btn');         // The button to generate flashcards
    const submitBtn = document.getElementById('submit-btn');
    const downloadBtn = document.getElementById('download-btn');
    const flashcardsContainer = document.getElementById('flashcards-container'); // The container where flashcards will be displayed

    let flashcards = [];

    // Add a click event listener to the generate button
    generateBtn.addEventListener('click', async function() {
        // Get the notes from the input field and remove any whitespace from the beginning and end
        const notes = notesInput.value.trim();
        
        // Check if the notes are empty
        if (!notes) {
            // Show an alert if no notes were provided
            alert('Please paste some notes first!');
            return; // Exit the function early
        }

        // Show loading message
        generateBtn.textContent = 'Loading...';  // Change button text to indicate loading
        generateBtn.disabled = true;             // Disable the button to prevent multiple clicks

        try {
            // Make an API request to the backend server
            const response = await fetch('http://localhost:8000/api/generate-flashcards', {
                method: 'POST',                  // Use POST HTTP method
                headers: {
                    'Content-Type': 'application/json'  // Set the content type to JSON
                },
                body: JSON.stringify({ text: notes })  // Using 'text' to match the backend API model
            });

            // Check if the response was successful
            if (!response.ok) {
                throw new Error('Network response was not ok');  // Throw an error if response wasn't successful
            }

            // Parse the JSON response from the server
            const responseData = await response.json();
            
            // Add debugging to see what's actually coming back
            console.log('Response from server:', responseData);
            
            // Check if the response contains the expected data structure
            if (responseData.status === 'success' && responseData.data) {
                console.log('Response data before parsing:', typeof responseData.data, responseData.data);
                try {
                    let jsonData = responseData.data;
                    
                    // Handle potential markdown code blocks in the response
                    if (typeof jsonData === 'string') {
                        // Remove markdown code block syntax if present
                        if (jsonData.includes('```json')) {
                            jsonData = jsonData.replace(/```json\n|\n```/g, '');
                        } else if (jsonData.includes('```')) {
                            jsonData = jsonData.replace(/```\n|\n```/g, '');
                        }
                        
                        // Try to parse the cleaned string
                        const parsedData = JSON.parse(jsonData);
                        console.log('Parsed data:', parsedData);
                        flashcards = parsedData;
                    } else if (typeof jsonData === 'object') {
                        // If it's already an object, use it directly
                        console.log('Data is already an object, using directly');
                        flashcards = jsonData;
                    }
                } catch (parseError) {
                    console.error('Error parsing response data:', parseError);
                    console.log('Response data that failed parsing:', responseData.data);
                    // If it's not valid JSON, let's try using it directly
                    if (typeof responseData.data === 'object' && Array.isArray(responseData.data)) {
                        console.log('Using data directly as it appears to be an array already');
                        flashcards = responseData.data;
                    } else {
                        flashcards = []; // Set empty array if parsing fails
                        throw new Error('Could not parse flashcard data from server response');
                    }
                }
            } else {
                // If response doesn't have the expected structure
                console.error('Unexpected response format:', responseData);
                flashcards = [];
                throw new Error('Unexpected response format from server');
            }

            // Generate HTML for each flashcard and update the container
            flashcardsContainer.innerHTML = flashcards.map(flashcard => `
                <div class="flashcard">
                    <div class="question">${flashcard.front}</div>  <!-- Display the front (question) of the flashcard -->
                    <div class="answer">${flashcard.back}</div>     <!-- Display the back (answer) of the flashcard -->
                </div>
            `).join('');  // Join all the HTML strings together

            // Show the submit and download buttons after flashcards are generated
            submitBtn.style.display = 'block';
            downloadBtn.style.display = 'block';
        } catch (error) {
            // Handle any errors that occurred during the fetch operation
            console.error('There was a problem with the fetch operation:', error);  // Log the error to the console
            flashcardsContainer.innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;  // Display error message to the user
        } finally {
            // Revert button to original state
            generateBtn.textContent = 'Generate Flashcards';  // Reset the button text
            generateBtn.disabled = false;                     // Re-enable the button
        }
    });

    submitBtn.addEventListener('click', async function() {
        if (flashcards.length === 0) {
            alert('No flashcards to submit. Please generate flashcards first.');
            return;
        }

        submitBtn.textContent = 'Submitting...';
        submitBtn.disabled = true;

        try {
            const response = await fetch('https://api.mochi.cards/decks', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer YOUR_MOCHI_API_KEY' // Replace with your Mochi API key
                },
                body: JSON.stringify({
                    name: 'New Flashcard Deck',
                    cards: flashcards
                })
            });

            if (!response.ok) {
                throw new Error('Failed to submit flashcards to Mochi');
            }

            alert('Flashcards successfully submitted to Mochi!');
        } catch (error) {
            console.error('There was a problem with the submission:', error);
            alert(`Error: ${error.message}`);
        } finally {
            submitBtn.textContent = 'Submit to Mochi';
            submitBtn.disabled = false;
        }
    });

    downloadBtn.addEventListener('click', function() {
        if (flashcards.length === 0) {
            alert('No flashcards to download. Please generate flashcards first.');
            return;
        }

        const blob = new Blob([JSON.stringify(flashcards, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'flashcards.json';
        a.click();
        URL.revokeObjectURL(url);
    });
}); 