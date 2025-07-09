import pytest
from rest_framework.test import APIClient
from backend.models import OTP

@pytest.fixture
def api_client():
    """Provide an instance of the APIClient."""
    return APIClient()

@pytest.mark.django_db
def test_signup_success(api_client):
    """Test successful signup with valid OTP."""
    # Create OTP record
    OTP.objects.create(email="newuser@example.com", otp="123456")

    payload = {
        "email": "newuser@example.com",
        "password": "newpassword",
        "name": "New User",
        "entity_name": "New Entity",
        "entity_type": "STARTUP",
        "otp": "123456"
    }
    response = api_client.post("/api/auth/signup/", payload)
    assert response.status_code == 201
    assert response.data["message"] == "User created successfully"

@pytest.mark.django_db
def test_signup_incorrect_otp(api_client):
    """Test signup with incorrect OTP."""
    # Create OTP record
    OTP.objects.create(email="newuser@example.com", otp="123456")

    payload = {
        "email": "newuser@example.com",
        "password": "newpassword",
        "name": "New User",
        "entity_name": "New Entity",
        "entity_type": "STARTUP",
        "otp": "654321"  # Incorrect OTP
    }
    response = api_client.post("/api/auth/signup/", payload)
    assert response.status_code == 400
    assert response.data["error"] == "Incorrect OTP"

@pytest.mark.django_db
def test_signup_missing_otp(api_client):
    """Test signup with missing OTP."""
    payload = {
        "email": "newuser@example.com",
        "password": "newpassword",
        "name": "New User",
        "entity_name": "New Entity",
        "entity_type": "STARTUP"
        # Missing OTP
    }
    response = api_client.post("/api/auth/signup/", payload)
    assert response.status_code == 400
    assert response.data["error"] == "OTP not found for this email"

@pytest.mark.django_db
def test_login_success(api_client):
    """Test successful login."""
    # Create a user
    signup_payload = {
        "email": "testuser@example.com",
        "password": "securepassword",
        "name": "Test User",
        "entity_name": "Test Entity",
        "entity_type": "STARTUP",
        "otp": "123456"
    }
    OTP.objects.create(email="testuser@example.com", otp="123456")
    api_client.post("/api/auth/signup/", signup_payload)

    # Login
    login_payload = {
        "email": "testuser@example.com",
        "password": "securepassword"
    }
    response = api_client.post("/api/auth/login/", login_payload)
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
    response = api_client.post("/api/auth/login/", payload)
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
        "entity_type": "STARTUP",
        "otp": "123456"
    }
    OTP.objects.create(email="testuser@example.com", otp="123456")
    api_client.post("/api/auth/signup/", signup_payload)

    login_payload = {
        "email": "testuser@example.com",
        "password": "securepassword"
    }
    login_response = api_client.post("/api/auth/login/", login_payload)
    assert login_response.status_code == 200
    assert "refresh" in login_response.data

    refresh_token = login_response.data["refresh"]

    # Logout
    logout_payload = {"refresh": refresh_token}
    response = api_client.post("/api/auth/logout/", logout_payload)
    assert response.status_code == 200
    assert response.data["message"] == "Logout successful"

@pytest.mark.django_db
def test_send_otp_success(api_client):
    """Test successful OTP sending."""
    payload = {"email": "testuser@example.com"}
    response = api_client.post("/api/auth/send-otp/", payload)
    assert response.status_code == 200
    assert response.data["message"] == "OTP sent successfully"

@pytest.mark.django_db
def test_send_otp_missing_email(api_client):
    """Test OTP sending with missing email."""
    payload = {}  # Missing email
    response = api_client.post("/api/auth/send-otp/", payload)
    assert response.status_code == 400
    assert response.data["error"] == "Email is required"