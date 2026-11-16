
from app.models.user import User
from app.core.security import hash_password


def setup_admin(db_session):
    admin = User(
        full_name="Movement Admin",
        email="movementadmin@test.com",
        hashed_password=hash_password("AdminPassword123"),
        role="admin",
        is_active=True
    )

    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)

    return admin


def setup_product_and_inventory(client, token):
    product_response = client.post(
        "/api/v1/products/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Movement Test Product",
            "sku": "MOV-TEST-001",
            "price": "500.00"
        }
    )

    assert product_response.status_code == 201

    product_id = product_response.json()["id"]

    inventory_response = client.post(
        "/api/v1/inventory/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "product_id": product_id,
            "quantity": 50,
            "reorder_level": 10
        }
    )

    assert inventory_response.status_code == 201

    return product_id


def get_token(client):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "movementadmin@test.com",
            "password": "AdminPassword123"
        }
    )

    return response.json()["access_token"]


def get_inventory_quantity(client, token, product_id):
    response = client.get(
        f"/api/v1/inventory/product/{product_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    return response.json()["quantity"]


def test_stock_in_movement(client, db_session):
    setup_admin(db_session)
    token = get_token(client)
    product_id = setup_product_and_inventory(client, token)

    response = client.post(
        "/api/v1/stock-movements/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "product_id": product_id,
            "movement_type": "IN",
            "quantity": 20,
            "reason": "Restocking"
        }
    )

    assert response.status_code == 201
    assert response.json()["quantity_before"] == 50
    assert response.json()["quantity_after"] == 70
    assert get_inventory_quantity(client, token, product_id) == 70


def test_stock_out_movement(client, db_session):
    setup_admin(db_session)
    token = get_token(client)
    product_id = setup_product_and_inventory(client, token)

    response = client.post(
        "/api/v1/stock-movements/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "product_id": product_id,
            "movement_type": "OUT",
            "quantity": 15,
            "reason": "Stock issued"
        }
    )

    assert response.status_code == 201
    assert response.json()["quantity_before"] == 50
    assert response.json()["quantity_after"] == 35
    assert get_inventory_quantity(client, token, product_id) == 35


def test_insufficient_stock_rejected(client, db_session):
    setup_admin(db_session)
    token = get_token(client)
    product_id = setup_product_and_inventory(client, token)

    response = client.post(
        "/api/v1/stock-movements/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "product_id": product_id,
            "movement_type": "OUT",
            "quantity": 100,
            "reason": "Insufficient stock test"
        }
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Insufficient stock available."

    # Failed movement must not change inventory.
    assert get_inventory_quantity(client, token, product_id) == 50


def test_stock_adjustment(client, db_session):
    setup_admin(db_session)
    token = get_token(client)
    product_id = setup_product_and_inventory(client, token)

    response = client.post(
        "/api/v1/stock-movements/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "product_id": product_id,
            "movement_type": "ADJUSTMENT",
            "quantity": 30,
            "reason": "Physical stock count"
        }
    )

    assert response.status_code == 201
    assert response.json()["quantity_before"] == 50
    assert response.json()["quantity_after"] == 30

    # The recorded movement is the difference: 20.
    assert response.json()["quantity"] == 20
    assert get_inventory_quantity(client, token, product_id) == 30


def test_zero_change_movement_rejected(client, db_session):
    setup_admin(db_session)
    token = get_token(client)
    product_id = setup_product_and_inventory(client, token)

    response = client.post(
        "/api/v1/stock-movements/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "product_id": product_id,
            "movement_type": "ADJUSTMENT",
            "quantity": 50,
            "reason": "No change test"
        }
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Stock movement would not change the quantity."
    )

    assert get_inventory_quantity(client, token, product_id) == 50
