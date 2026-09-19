import os
from dotenv import load_dotenv

# Project settings
PROJECT_NAME = "Gym FAQ Chatbot"

# File paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
FAQ_FILE = os.path.join(DATA_DIR, 'faqs.csv')

# Load optional .env overrides (see .env.example)
load_dotenv(os.path.join(BASE_DIR, '.env'))


def _as_bool(value, default):
    if value is None:
        return default
    return str(value).strip().lower() in ('1', 'true', 'yes', 'on')


# Flask app
DEBUG = _as_bool(os.getenv('DEBUG'), True)
PORT = int(os.getenv('PORT', '5000'))

# Similarity matching
SIMILARITY_THRESHOLD = float(os.getenv('SIMILARITY_THRESHOLD', '0.25'))
MAX_RESULTS = int(os.getenv('MAX_RESULTS', '3'))

# Console verbosity (startup banners / emoji status lines)
VERBOSE = _as_bool(os.getenv('VERBOSE'), False)