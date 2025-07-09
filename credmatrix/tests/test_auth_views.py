import pytest
from rest_framework.test import APIClient

@pytest.fixture
def api_client():
    """Provide an instance of the APIClient."""
    return APIClient()

@pytest.mark.django_db
def test_signup_success(api_client):
    """Test successful signup."""
    payload = {
        "email": "newuser@example.com",
        "password": "newpassword",
        "name": "New User",
        "entity_name": "New Entity",
        "entity_type": "STARTUP"
    }
    response = api_client.post("/api/signup/", payload)
    assert response.status_code == 201
    assert response.data["message"] == "User created successfully"

@pytest.mark.django_db
def test_login_success(api_client):
    """Test successful login."""
    # Create a user
    signup_payload = {
        "email": "testuser@example.com",
        "password": "securepassword",
        "name": "Test User",
        "entity_name": "Test Entity",
        "entity_type": "STARTUP"
    }
    api_client.post("/api/signup/", signup_payload)

    # Login
    login_payload = {
        "email": "testuser@example.com",
        "password": "securepassword"
    }
    response = api_client.post("/api/login/", login_payload)
    assert response.status_code == 200
    assert "access" in response.data
    assert "refresh" in response.data

@pytest.mark.django_db
def test_login_invalid_credentials(api_client):
    """Test login with invalid credentials."""
    payload = {
        "email": "nonexistentuser@example.com",
        "password": "wrongpassword"
    }
    response = api_client.post("/api/login/", payload)
    assert response.status_code == 401
    assert response.data["error"] == "Invalid credentials"

@pytest.mark.django_db
def test_logout_success(api_client):
    """Test successful logout."""
    # Create a user and log in
    signup_payload = {
        "email": "testuser@example.com",
        "password": "securepassword",
        "name": "Test User",
        "entity_name": "Test Entity",
        "entity_type": "STARTUP"
    }
    api_client.post("/api/signup/", signup_payload)

    login_payload = {
        "email": "testuser@example.com",
        "password": "securepassword"
    }
    login_response = api_client.post("/api/login/", login_payload)
    assert login_response.status_code == 200
    assert "refresh" in login_response.data

    refresh_token = login_response.data["refresh"]

    # Logout
    logout_payload = {"refresh": refresh_token}
    response = api_client.post("/api/logout/", logout_payload)
    assert response.status_code == 200
    assert response.data["message"] == "Logout successful"

@pytest.mark.django_db
def test_send_otp_success(api_client):
    """Test successful OTP sending."""
    # Create a user
    signup_payload = {
        "email": "testuser@example.com",
        "password": "securepassword",
        "name": "Test User",
        "entity_name": "Test Entity",
        "entity_type": "STARTUP"
    }
    api_client.post("/api/signup/", signup_payload)

    # Send OTP
    payload = {"email": "testuser@example.com"}
    response = api_client.post("/api/send_otp/", payload)
    assert response.status_code == 200
    assert response.data["message"] == "OTP sent successfully"