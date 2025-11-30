// chatbot.js
// This API endpoint MUST match the host and port your Python Flask server is running on.
const API_ENDPOINT = 'http://127.0.0.1:5000/chat';

// Helper function to create and append message elements
function displayMessage(text, sender) {
    const chatWindow = document.getElementById('chat-window');
    if (!chatWindow) return; // Ensure the element exists

    const msgElement = document.createElement('p');
    msgElement.classList.add('message');
    msgElement.classList.add(sender === 'bot'? 'bot-message' : 'user-message');
    msgElement.textContent = text;
    chatWindow.appendChild(msgElement);
    chatWindow.scrollTop = chatWindow.scrollHeight; // Auto-scroll
}

async function sendMessage() {
    const chatInput = document.getElementById('chat-input');
    const userInput = chatInput.value.trim();

    if (userInput === '') return;

    // 1. Display user message and clear input
    displayMessage(userInput, 'user');
    chatInput.value = '';

    // 2. Send request to the Python API
    try {
        const payload = {
            message: userInput // Package the user's text into a JSON object
        };

        const response = await fetch(API_ENDPOINT, { // <-- THIS IS THE CALL TO THE BACKEND
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload) // Convert JavaScript object to JSON string
        });

        // 3. Handle non-200 HTTP responses (network or server error)
        if (!response.ok) {
            throw new Error(`Server returned status code: ${response.status}`);
        }

        // 4. Parse JSON response from Python
        const data = await response.json();

        // 5. Display the Python-generated response
        // This is the line that had the error. The pipe symbol must be double (||) for logical OR.
        displayMessage(data.response || "No response received from the bot.", 'bot');

    } catch (error) {
        console.error('API Communication Error:', error);
        displayMessage('System Error', 'Cannot connect to the Python Chatbot service. Ensure app.py is running.', 'bot');
    }
}

// Attach event listener to the input field once the DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const chatInput = document.getElementById('chat-input');

    if (chatInput) {
        chatInput.addEventListener('keydown', function(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        });

        // Initial welcome message (local JS for instant feedback)
        setTimeout(() => {
            displayMessage(`Hello! I am the Q&A bot for Marcus Jackson. Try: start guided Q&A`, 'bot');
        }, 100);
    }
});