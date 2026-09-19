import pandas as pd
import sys
from pathlib import Path

# Make the project root importable for both direct execution and package import
_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

try:
    from .utils import ensure_utf8_console
except ImportError:
    from utils import ensure_utf8_console

# Fix Windows console crash - enable UTF-8 output for emoji print statements
ensure_utf8_console()

# Handle imports for both direct execution and package import
try:
    from .preprocessing import TextPreprocessor
    from .similarity import SimilarityMatcher
except ImportError:
    # For direct execution (testing)
    from preprocessing import TextPreprocessor
    from similarity import SimilarityMatcher

from config.settings import FAQ_FILE, MAX_RESULTS, SIMILARITY_THRESHOLD, VERBOSE


def _log(*args):
    """Print only when VERBOSE is enabled (keeps default startup quiet)."""
    if VERBOSE:
        print(*args)

# Generic one-word queries that are too ambiguous for TF-IDF (short-document
# bias would pick e.g. "trial class" for "classes"), pinned to the right FAQ id.
INTENT_OVERRIDES = {
    'class': 28,   # "classes" / "class"
    'facil': 23,   # "facilities" / "facility"
}

class FAQChatbot:
    """
    Main Chatbot class that orchestrates preprocessing and matching
    """
    def __init__(self, faq_file):
        """
        Initialize chatbot with FAQ data
        
        Args:
            faq_file (str): Path to CSV file with FAQs
        """
        _log("📚 Loading FAQs...")
        
        # FIX: Convert to absolute path (works from any directory)
        faq_path = Path(faq_file)
        if not faq_path.is_absolute():
            # If relative path, make it relative to this file's location
            faq_path = Path(__file__).resolve().parent.parent / faq_file
        
        # Load FAQ data
        self.faqs = pd.read_csv(faq_path)
        
        _log(f"✅ Loaded {len(self.faqs)} FAQs")
        
        # Initialize text preprocessor
        _log("🧹 Initializing text preprocessor...")
        self.preprocessor = TextPreprocessor()
        
        # Preprocess all FAQ questions
        self.faqs['processed_question'] = self.faqs['question'].apply(
            self.preprocessor.clean_text
        )
        
        # Preprocess all FAQ answers (used to widen matching vocabulary)
        self.faqs['processed_answer'] = self.faqs['answer'].apply(
            self.preprocessor.clean_text
        )
        
        # Preprocess curated keywords when present (preferred matching signal)
        if 'keywords' in self.faqs.columns:
            self.faqs['processed_keywords'] = (
                self.faqs['keywords'].fillna('').apply(self.preprocessor.clean_text)
            )
        
        # Initialize similarity matcher
        _log("🔍 Initializing similarity matcher...")
        self.matcher = SimilarityMatcher(self.faqs)
        
        print(f"FAQChatbot ready: {len(self.faqs)} FAQs loaded")
    
    def get_response(self, user_question, top_k=MAX_RESULTS, threshold=SIMILARITY_THRESHOLD):
        """
        Get chatbot response to user question
        
        Args:
            user_question (str): Raw user question
            top_k (int): Number of results to consider (default: from settings)
            threshold (float): Minimum similarity threshold (default: from settings)
            
        Returns:
            dict: Response with answer, confidence, and status
        """
        # Preprocess user question
        processed_question = self.preprocessor.clean_text(user_question)
        
        # Direct intent override for generic one-word queries
        override_id = INTENT_OVERRIDES.get(processed_question)
        if override_id is not None:
            override_rows = self.faqs[self.faqs['id'] == override_id]
            if not override_rows.empty:
                row = override_rows.iloc[0]
                return {
                    'answer': row['answer'],
                    'confidence': '100.0%',
                    'category': row['category'],
                    'faq_id': int(row['id']),
                    'status': 'success'
                }
        
        # Find matches with improved settings
        matches = self.matcher.find_best_match(
            processed_question,
            top_k=top_k,
            threshold=threshold
        )
        
        # Prepare response
        if matches:
            best_match = matches[0]
            return {
                'answer': best_match['answer'],
                'confidence': f"{best_match['similarity']*100:.1f}%",
                'category': best_match['category'],
                'faq_id': int(self.faqs.iloc[best_match['index']]['id']),
                'status': 'success'
            }
        else:
            return {
                'answer': "I couldn't find an exact match, but I can help with questions about gym timings, memberships, classes, facilities, trainers, peak hours, payment, policies, and more! Try asking: 'What are gym timings?' or 'Hey mate' for gym details!",
                'confidence': '0%',
                'category': 'unknown',
                'status': 'no_match'
            }


# Test the chatbot
if __name__ == "__main__":
    # Initialize chatbot
    chatbot = FAQChatbot(FAQ_FILE)
    
    # Test conversations with improved test cases
    test_questions = [
        "Hey mate",
        "What are the gym timings?",
        "How many trainers?",
        "Peak timing?",
        "How much membership cost?",
        "Can I freeze membership?",
        "Do you have a sauna?",
        "Tell me about gym",
    ]
    
    print("=" * 70)
    print("💬 IMPROVED CHATBOT TEST CONVERSATION")
    print("=" * 70)
    
    for question in test_questions:
        print(f"\n👤 User: {question}")
        
        response = chatbot.get_response(question)
        
        print(f"🤖 Bot: {response['answer']}")
        print(f"📊 Confidence: {response['confidence']} | Category: {response['category']}")
        print("-" * 70)