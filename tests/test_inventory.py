
from app.models.user import User
from app.core.security import hash_password


def setup_admin(db_session):
    admin = User(
        full_name="Inventory Admin",
        email="inventoryadmin@test.com",
        hashed_password=hash_password("AdminPassword123"),
        role="admin",
        is_active=True
    )

    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)

    return admin


def setup_product(client, token):
    response = client.post(
        "/api/v1/products/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Inventory Test Product",
            "sku": "INV-TEST-001",
            "price": "1000.00"
        }
    )

    assert response.status_code == 201
    return response.json()["id"]


def setup_inventory(client, token, product_id, quantity=50):
    return client.post(
        "/api/v1/inventory/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "product_id": product_id,
            "quantity": quantity,
            "reorder_level": 10
        }
    )


def test_create_inventory(client, db_session):
    setup_admin(db_session)
    token = client.post(
        "/api/v1/auth/login",
        json={
            "email": "inventoryadmin@test.com",
            "password": "AdminPassword123"
        }
    ).json()["access_token"]

    product_id = setup_product(client, token)

    response = setup_inventory(
        client, token, product_id, quantity=50
    )

    assert response.status_code == 201
    assert response.json()["quantity"] == 50
    assert response.json()["reorder_level"] == 10


def test_duplicate_inventory_rejected(client, db_session):
    setup_admin(db_session)
    token = client.post(
        "/api/v1/auth/login",
        json={
            "email": "inventoryadmin@test.com",
            "password": "AdminPassword123"
        }
    ).json()["access_token"]

    product_id = setup_product(client, token)

    first = setup_inventory(client, token, product_id)
    second = setup_inventory(client, token, product_id)

    assert first.status_code == 201
    assert second.status_code == 409


def test_update_inventory(client, db_session):
    setup_admin(db_session)
    token = client.post(
        "/api/v1/auth/login",
        json={
            "email": "inventoryadmin@test.com",
            "password": "AdminPassword123"
        }
    ).json()["access_token"]

    product_id = setup_product(client, token)
    created = setup_inventory(client, token, product_id)

    inventory_id = created.json()["id"]

    response = client.put(
        f"/api/v1/inventory/{inventory_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "quantity": 75,
            "reorder_level": 15
        }
    )

    assert response.status_code == 200
    assert response.json()["quantity"] == 75
    assert response.json()["reorder_level"] == 15


def test_low_stock_inventory(client, db_session):
    setup_admin(db_session)
    token = client.post(
        "/api/v1/auth/login",
        json={
            "email": "inventoryadmin@test.com",
            "password": "AdminPassword123"
        }
    ).json()["access_token"]

    product_id = setup_product(client, token)
    setup_inventory(client, token, product_id, quantity=5)

    response = client.get(
        "/api/v1/inventory/low-stock",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["quantity"] == 5
