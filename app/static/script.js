// ============================================================
// GYM FAQ CHATBOT - FRONTEND SCRIPT
// ============================================================

/**
 * Send user message to chatbot
 */
function sendMessage() {
    const userInput = document.getElementById('userInput');
    const message = userInput.value.trim();
    
    // Validate input
    if (!message) {
        userInput.focus();
        return;
    }
    
    // Display user message
    displayMessage(message, 'user');
    
    // Clear input
    userInput.value = '';
    
    // Show typing indicator
    showTypingIndicator(true);
    
    // Disable send button
    document.getElementById('sendBtn').disabled = true;
    
    // Send to backend
    fetch('/api/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: message })
    })
    .then(response => response.json())
    .then(data => {
        // Hide typing indicator
        showTypingIndicator(false);
        
        // Display bot response
        displayMessage(data.answer, 'bot', data);
    })
    .catch(error => {
        console.error('Error:', error);
        showTypingIndicator(false);
        displayMessage('Sorry, something went wrong! Please try again.', 'bot', {
            category: 'error',
            confidence: '0%'
        });
    })
    .finally(() => {
        // Enable send button
        document.getElementById('sendBtn').disabled = false;
        userInput.focus();
    });
}

/**
 * Display a message in the chat box
 * @param {string} text - Message text
 * @param {string} sender - 'user' or 'bot'
 * @param {object} data - Additional data (confidence, category)
 */
function displayMessage(text, sender, data = {}) {
    const chatBox = document.getElementById('chatBox');
    
    // Create message container
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    // Create message content
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = text;
    messageDiv.appendChild(contentDiv);
    
    // Create message meta (category and confidence)
    if (sender === 'bot' && data.category) {
        const metaDiv = document.createElement('div');
        metaDiv.className = 'message-meta';
        
        let metaText = `Category: ${data.category}`;
        if (data.confidence) {
            metaText += ` | Confidence: ${data.confidence}`;
        }
        
        metaDiv.textContent = metaText;
        messageDiv.appendChild(metaDiv);
    }
    
    // Add to chat box
    chatBox.appendChild(messageDiv);
    
    // Auto-scroll to bottom
    chatBox.scrollTop = chatBox.scrollHeight;
}

/**
 * Show/hide typing indicator
 * @param {boolean} show - True to show, false to hide
 */
function showTypingIndicator(show) {
    const indicator = document.getElementById('typingIndicator');
    if (show) {
        indicator.style.display = 'flex';
        // Auto-scroll to show typing indicator
        const chatBox = document.getElementById('chatBox');
        chatBox.scrollTop = chatBox.scrollHeight;
    } else {
        indicator.style.display = 'none';
    }
}

/**
 * Handle Enter key press in input field
 */
document.addEventListener('DOMContentLoaded', function() {
    const userInput = document.getElementById('userInput');
    
    // Send message on Enter key
    userInput.addEventListener('keypress', function(event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            sendMessage();
        }
    });
    
    // Focus on input when page loads
    userInput.focus();
});