
from app.models.user import User
from app.core.security import hash_password


def create_admin(db_session):
    admin = User(
        full_name="Test Admin",
        email="admin@test.com",
        hashed_password=hash_password("AdminPassword123"),
        role="admin",
        is_active=True
    )

    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)

    return admin


def get_admin_token(client):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "admin@test.com",
            "password": "AdminPassword123"
        }
    )

    assert response.status_code == 200

    return response.json()["access_token"]


def test_create_product(client, db_session):
    create_admin(db_session)
    token = get_admin_token(client)

    response = client.post(
        "/api/v1/products/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Test Keyboard",
            "sku": "TEST-KB-001",
            "description": "Testing product creation",
            "price": "1500.00"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Test Keyboard"
    assert data["sku"] == "TEST-KB-001"
    assert data["is_active"] is True


def test_get_all_products(client, db_session):
    create_admin(db_session)
    token = get_admin_token(client)

    client.post(
        "/api/v1/products/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Test Mouse",
            "sku": "TEST-MS-001",
            "price": "800.00"
        }
    )

    response = client.get(
        "/api/v1/products/",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert len(data["products"]) == 1
    assert data["products"][0]["sku"] == "TEST-MS-001"


def test_get_product_by_id(client, db_session):
    create_admin(db_session)
    token = get_admin_token(client)

    create_response = client.post(
        "/api/v1/products/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Test Monitor",
            "sku": "TEST-MN-001",
            "price": "12000.00"
        }
    )

    product_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/products/{product_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["id"] == product_id


def test_update_product(client, db_session):
    create_admin(db_session)
    token = get_admin_token(client)

    create_response = client.post(
        "/api/v1/products/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Old Keyboard",
            "sku": "TEST-KB-002",
            "price": "1000.00"
        }
    )

    product_id = create_response.json()["id"]

    response = client.put(
        f"/api/v1/products/{product_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Updated Keyboard",
            "sku": "TEST-KB-002",
            "price": "1800.00"
        }
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Updated Keyboard"
    assert response.json()["price"] == "1800.00"


def test_duplicate_product_sku(client, db_session):
    create_admin(db_session)
    token = get_admin_token(client)

    headers = {"Authorization": f"Bearer {token}"}

    product_data = {
        "name": "First Product",
        "sku": "DUPLICATE-001",
        "price": "500.00"
    }

    first_response = client.post(
        "/api/v1/products/",
        headers=headers,
        json=product_data
    )

    second_response = client.post(
        "/api/v1/products/",
        headers=headers,
        json={
            "name": "Second Product",
            "sku": "DUPLICATE-001",
            "price": "700.00"
        }
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_delete_product(client, db_session):
    create_admin(db_session)
    token = get_admin_token(client)

    headers = {"Authorization": f"Bearer {token}"}

    create_response = client.post(
        "/api/v1/products/",
        headers=headers,
        json={
            "name": "Delete Test",
            "sku": "DELETE-001",
            "price": "500.00"
        }
    )

    product_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/api/v1/products/{product_id}",
        headers=headers
    )

    assert delete_response.status_code == 200
    assert delete_response.json()["is_active"] is False

    get_response = client.get(
        f"/api/v1/products/{product_id}",
        headers=headers
    )

    assert get_response.status_code == 404
