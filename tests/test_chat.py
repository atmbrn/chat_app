import pytest
from fastapi.testclient import TestClient
from main import app
from auth import create_access_token

client = TestClient(app)

def test_token_generation_and_auth():
    token = create_access_token({"sub": "testuser"})
    assert isinstance(token, str)

def test_websocket_auth():
    token = create_access_token({"sub": "testuser"})
    with client.websocket_connect(f"/ws/chat?token={token}") as websocket:
        websocket.send_text("Hello <script>alert(1)</script>")
