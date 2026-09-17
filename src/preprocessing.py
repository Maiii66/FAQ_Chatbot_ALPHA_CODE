import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re

# Download required NLTK data (run once)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')


class TextPreprocessor:
    """
    Preprocesses text for NLP tasks:
    - Converts to lowercase
    - Removes special characters
    - Tokenizes (splits into words)
    - Removes stopwords (the, a, is, etc.)
    """
    
    def __init__(self):
        """Initialize the preprocessor with English stopwords"""
        self.stop_words = set(stopwords.words('english'))
    
    def clean_text(self, text):
        """
        Clean and preprocess text
        
        Args:
            text (str): Raw text to clean
            
        Returns:
            str: Cleaned text
        """
        # Step 1: Convert to lowercase
        text = text.lower()
        
        # Step 2: Remove special characters (keep only letters, numbers, spaces)
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        
        # Step 3: Remove extra whitespace
        text = text.strip()
        
        # Step 4: Tokenize (split into words)
        tokens = word_tokenize(text)
        
        # Step 5: Remove stopwords
        tokens = [t for t in tokens if t not in self.stop_words and len(t) > 1]
        
        # Step 6: Join back into string
        cleaned_text = ' '.join(tokens)
        
        return cleaned_text


# Test the preprocessor
if __name__ == "__main__":
    processor = TextPreprocessor()
    
    # Test cases
    test_texts = [
        "How do I reset my PASSWORD???",
        "What's the REFUND policy?",
        "I forgot my password, how to change it?"
    ]
    
    print("🧹 TEXT PREPROCESSING TESTS:\n")
    for text in test_texts:
        cleaned = processor.clean_text(text)
        print(f"Original: {text}")
        print(f"Cleaned:  {cleaned}\n")