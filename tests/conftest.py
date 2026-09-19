import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture(scope="session")
def chatbot():
    from config.settings import FAQ_FILE
    from src.chatbot import FAQChatbot
    return FAQChatbot(FAQ_FILE)