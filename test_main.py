import sys
from unittest.mock import MagicMock

# Mock database module before importing main
import database
database.create_tables = MagicMock()
database.get_connection = MagicMock()
database.get_jobs = MagicMock(return_value=[
    {"id": 1, "title": "Software Engineer", "company": "Google", "description": "Backend dev"}
])
database.get_user_by_email = MagicMock(return_value=None)
database.create_user = MagicMock(return_value=1)
database.add_application = MagicMock(return_value=True)

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_login_page():
    response = client.get("/")
    assert response.status_code == 200
    assert "Login" in response.text or "login" in response.text.lower()

def test_register_page():
    response = client.get("/register")
    assert response.status_code == 200
    assert "Register" in response.text or "register" in response.text.lower()

def test_jobs_page_without_login():
    # FastAPI/Starlette redirects return status_code 303 or 302
    response = client.get("/jobs", follow_redirects=False)
    assert response.status_code in [302, 303]
