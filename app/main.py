from flask import Flask, render_template, request, jsonify
import sys
import os

# Add parent directory to path so we can import src
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.chatbot import FAQChatbot
from config.settings import FAQ_FILE, PORT, DEBUG, VERBOSE, MAX_RESULTS, SIMILARITY_THRESHOLD

# Initialize Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')

# Initialize chatbot (runs once when app starts)
if VERBOSE:
    print("\n" + "="*60)
    print("🚀 INITIALIZING GYM FAQ CHATBOT")
    print("="*60)
chatbot = FAQChatbot(FAQ_FILE)
print(f"✅ Flask app ready! Visit http://localhost:{PORT}")
if VERBOSE:
    print("="*60 + "\n")


@app.route('/')
def home():
    """
    Serve the main chat page
    """
    return render_template('index.html')


@app.route('/api/chat', methods=['POST'])
def chat():
    """
    API endpoint that processes user messages
    
    Expected JSON: {"message": "user question"}
    Returns JSON: {"answer": "...", "confidence": "...", "category": "..."}
    """
    try:
        # Get user message from request
        data = request.json
        user_message = data.get('message', '').strip()
        
        # Validate message
        if not user_message:
            return jsonify({
                'answer': 'Please ask a question!',
                'confidence': '0%',
                'category': 'error',
                'status': 'error'
            }), 400
        
        # Get chatbot response
        response = chatbot.get_response(user_message, top_k=MAX_RESULTS, threshold=SIMILARITY_THRESHOLD)
        
        return jsonify(response), 200
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({
            'answer': f'Sorry, something went wrong: {str(e)}',
            'confidence': '0%',
            'category': 'error',
            'status': 'error'
        }), 500


@app.route('/api/health', methods=['GET'])
def health():
    """
    Health check endpoint
    """
    return jsonify({
        'status': 'healthy',
        'faqs_loaded': len(chatbot.faqs)
    }), 200


if __name__ == '__main__':
    # Run Flask app
    # DEBUG comes from config/settings.py (set DEBUG=false in .env for production)
    app.run(
        debug=DEBUG,
        host='127.0.0.1',
        port=PORT,
        use_reloader=False
    )