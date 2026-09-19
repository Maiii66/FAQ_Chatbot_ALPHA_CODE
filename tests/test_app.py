import pytest


@pytest.fixture
def client():
    from app.main import app
    app.config.update(TESTING=True)
    return app.test_client()


def test_home(client):
    resp = client.get("/")
    assert resp.status_code == 200


def test_health(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "healthy"
    assert data["faqs_loaded"] > 0


def test_chat_success(client):
    resp = client.post("/api/chat", json={"message": "What are the gym timings?"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "success"
    assert data["faq_id"] == 20


def test_chat_empty_message(client):
    resp = client.post("/api/chat", json={"message": "    "})
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["status"] == "error"