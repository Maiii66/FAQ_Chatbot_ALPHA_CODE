import os

# Project settings
PROJECT_NAME = "Gym FAQ Chatbot"
DEBUG = True
PORT = 5000

# File paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
FAQ_FILE = os.path.join(DATA_DIR, 'faqs.csv')

# Similarity threshold
SIMILARITY_THRESHOLD = 0.25  # 25% minimum match (aligned with chatbot default)
MAX_RESULTS = 3  # Show top 3 results