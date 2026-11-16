
from app.models.user import User
from app.core.security import hash_password


def create_admin(db_session):
    admin = User(
        full_name="Test Admin",
        email="admin.customers@test.com",
        hashed_password=hash_password("AdminPass123"),
        role="admin",
        is_active=True
    )
    db_session.add(admin)
    db_session.commit()
    return admin


def get_admin_headers(client):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "admin.customers@test.com",
            "password": "AdminPass123"
        }
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_customer(client, db_session):
    create_admin(db_session)
    headers = get_admin_headers(client)

    response = client.post(
        "/api/v1/customers/",
        json={
            "name": "Rahul Sharma",
            "email": "rahul.customer@test.com",
            "phone": "9876543210",
            "address": "Bengaluru"
        },
        headers=headers
    )

    assert response.status_code == 201
    assert response.json()["name"] == "Rahul Sharma"
    assert response.json()["email"] == "rahul.customer@test.com"
    assert response.json()["is_active"] is True


def test_get_all_customers(client, db_session):
    create_admin(db_session)
    headers = get_admin_headers(client)

    client.post(
        "/api/v1/customers/",
        json={"name": "Rahul Sharma"},
        headers=headers
    )

    response = client.get("/api/v1/customers/", headers=headers)

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_customer_by_id(client, db_session):
    create_admin(db_session)
    headers = get_admin_headers(client)

    create_response = client.post(
        "/api/v1/customers/",
        json={"name": "Rahul Sharma"},
        headers=headers
    )
    customer_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/customers/{customer_id}",
        headers=headers
    )

    assert response.status_code == 200
    assert response.json()["id"] == customer_id


def test_update_customer(client, db_session):
    create_admin(db_session)
    headers = get_admin_headers(client)

    create_response = client.post(
        "/api/v1/customers/",
        json={"name": "Rahul Sharma"},
        headers=headers
    )
    customer_id = create_response.json()["id"]

    response = client.put(
        f"/api/v1/customers/{customer_id}",
        json={"name": "Rahul Updated"},
        headers=headers
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Rahul Updated"


def test_delete_customer(client, db_session):
    create_admin(db_session)
    headers = get_admin_headers(client)

    create_response = client.post(
        "/api/v1/customers/",
        json={"name": "Rahul Sharma"},
        headers=headers
    )
    customer_id = create_response.json()["id"]

    response = client.delete(
        f"/api/v1/customers/{customer_id}",
        headers=headers
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is False

    get_response = client.get(
        f"/api/v1/customers/{customer_id}",
        headers=headers
    )

    assert get_response.status_code == 404


def test_customer_creation_requires_admin(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Staff User",
            "email": "staff.customers@test.com",
            "password": "StaffPass123"
        }
    )
    assert response.status_code == 201

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "staff.customers@test.com",
            "password": "StaffPass123"
        }
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(
        "/api/v1/customers/",
        json={"name": "Unauthorized Customer"},
        headers=headers
    )

    assert response.status_code == 403
