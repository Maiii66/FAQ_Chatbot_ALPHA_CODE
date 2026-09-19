import pytest

from config.settings import SIMILARITY_THRESHOLD
from tests.eval import CASES

_IDS = [question for question, _ in CASES]


@pytest.mark.parametrize("query,expected", CASES, ids=_IDS)
def test_accuracy(chatbot, query, expected):
    response = chatbot.get_response(query, top_k=1, threshold=SIMILARITY_THRESHOLD)
    match_id = response["faq_id"] if response["status"] == "success" else None

    if expected is None:
        assert match_id is None
    else:
        assert match_id in expected