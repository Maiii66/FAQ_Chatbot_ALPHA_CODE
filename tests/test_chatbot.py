from config.settings import MAX_RESULTS, SIMILARITY_THRESHOLD


def test_success_response(chatbot):
    response = chatbot.get_response("What are the gym timings?")
    assert response["status"] == "success"
    assert response["faq_id"] == 20
    assert response["confidence"].endswith("%")
    assert response["category"]


def test_greeting(chatbot):
    response = chatbot.get_response("hey mate")
    assert response["status"] == "success"
    assert response["faq_id"] == 6


def test_no_match(chatbot):
    response = chatbot.get_response("asdfgh jklmn")
    assert response["status"] == "no_match"
    assert response["confidence"] == "0%"
    assert response["category"] == "unknown"


def test_intent_override(chatbot):
    response = chatbot.get_response("classes")
    assert response["faq_id"] == 28

    response = chatbot.get_response("facilities")
    assert response["faq_id"] == 23


def test_threshold_rejects_weak_matches(chatbot):
    response = chatbot.get_response("asdfgh jklmn", threshold=0.99)
    assert response["status"] == "no_match"


def test_settings_defaults_apply():
    assert MAX_RESULTS > 0
    assert 0.0 < SIMILARITY_THRESHOLD < 1.0