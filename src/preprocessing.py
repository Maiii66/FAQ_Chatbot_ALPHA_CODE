import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import re
import sys
import io

# Fix Windows console crash when running this module directly (emoji prints)
if (sys.platform == 'win32' and hasattr(sys.stdout, 'buffer')
        and 'utf-8' not in (getattr(sys.stdout, 'encoding', '') or '').lower()):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Map everyday user vocabulary to the words used in the FAQ questions.
# Applied identically to both FAQ rows and user input, so the two now line up.
SYNONYMS = {
    'price': 'cost', 'prices': 'cost', 'pricing': 'cost',
    'close': 'timing', 'closes': 'timing', 'closing': 'timing',
    'closed': 'timing', 'timings': 'timing', 'time': 'timing',
    'times': 'timing', 'hour': 'timing', 'hours': 'timing',
    'pause': 'freeze', 'paused': 'freeze', 'pausing': 'freeze',
    'weekend': 'holiday', 'weekends': 'holiday',
    'diet': 'nutrition', 'diets': 'nutrition',
    'protein': 'supplement', 'proteins': 'supplement',
    'corona': 'covid', 'coronavirus': 'covid',
}

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
        """Initialize the preprocessor with English stopwords and a stemmer"""
        self.stop_words = set(stopwords.words('english')) | {
            'have', 'has', 'had', 'want', 'wants', 'need', 'needs',
            'give', 'show', 'tell', 'know', 'please', 'get',
            'something', 'anything', 'available',
        }
        self.stemmer = PorterStemmer()
    
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
        
        # Step 2: Normalize special tokens before punctuation stripping
        text = text.replace('24/7', '247').replace('24x7', '247').replace('24-7', '247')
        text = re.sub(r'covid[\s-]?19', 'covid', text)
        
        # Step 3: Replace punctuation with spaces (NOT delete, so words don't merge:
        # "first-aid" -> "first aid", "music/noise" -> "music noise", "co-ed" -> "co ed")
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
        
        # Step 4: Collapse extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Step 5: Tokenize (split into words)
        tokens = word_tokenize(text)
        
        # Step 6: Normalize synonyms so user wording matches FAQ wording
        tokens = [SYNONYMS.get(t, t) for t in tokens]
        
        # Step 7: Remove stopwords
        tokens = [t for t in tokens if t not in self.stop_words and len(t) > 1]
        
        # Step 8: Stem tokens so plurals/tenses match (beginner -> beginner, timings -> timing)
        tokens = [self.stemmer.stem(t) for t in tokens]
        
        # Step 9: Join back into string
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