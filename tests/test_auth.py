
def test_register_user(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Test User",
            "email": "testuser@example.com",
            "password": "TestPassword123"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["full_name"] == "Test User"
    assert data["email"] == "testuser@example.com"
    assert data["role"] == "staff"
    assert data["is_active"] is True
    assert "password" not in data


def test_register_duplicate_email(client):
    user_data = {
        "full_name": "Test User",
        "email": "duplicate@example.com",
        "password": "TestPassword123"
    }

    first_response = client.post(
        "/api/v1/auth/register",
        json=user_data
    )

    second_response = client.post(
        "/api/v1/auth/register",
        json=user_data
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_login_success(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Login User",
            "email": "login@example.com",
            "password": "LoginPassword123"
        }
    )

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "login@example.com",
            "password": "LoginPassword123"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Login User",
            "email": "wrongpassword@example.com",
            "password": "CorrectPassword123"
        }
    )

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "wrongpassword@example.com",
            "password": "WrongPassword123"
        }
    )

    assert response.status_code == 401

    assert response.json()["detail"] == "Invalid email or password."


def test_login_nonexistent_user(client):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "unknown@example.com",
            "password": "UnknownPassword123"
        }
    )

    assert response.status_code == 401
