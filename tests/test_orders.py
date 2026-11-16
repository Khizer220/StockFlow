
from decimal import Decimal

from app.models.user import User
from app.models.customer import Customer
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.stock_movement import StockMovement
from app.core.security import hash_password


def create_admin(db_session):
    admin = User(
        full_name="Test Admin",
        email="admin.orders@test.com",
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
            "email": "admin.orders@test.com",
            "password": "AdminPass123"
        }
    )

    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def setup_order_data(db_session, quantity=50):
    customer = Customer(
        name="Test Customer",
        email="customer.orders@test.com"
    )

    product = Product(
        name="Test Product",
        sku="ORDER-TEST-001",
        price=Decimal("100.00"),
        is_active=True
    )

    db_session.add_all([customer, product])
    db_session.flush()

    inventory = Inventory(
        product_id=product.id,
        quantity=quantity,
        reorder_level=10
    )

    db_session.add(inventory)
    db_session.commit()

    return customer, product, inventory


def test_create_order_and_deduct_stock(client, db_session):
    create_admin(db_session)
    headers = get_admin_headers(client)

    customer, product, inventory = setup_order_data(db_session)

    response = client.post(
        "/api/v1/orders/",
        json={
            "customer_id": customer.id,
            "items": [
                {
                    "product_id": product.id,
                    "quantity": 5
                }
            ]
        },
        headers=headers
    )

    assert response.status_code == 201

    order = response.json()

    assert order["customer_id"] == customer.id
    assert order["status"] == "PENDING"
    assert Decimal(str(order["total_amount"])) == Decimal("500.00")
    assert len(order["items"]) == 1

    db_session.refresh(inventory)
    assert inventory.quantity == 45

    movement = db_session.query(StockMovement).first()

    assert movement is not None
    assert movement.movement_type == "OUT"
    assert movement.quantity_before == 50
    assert movement.quantity_after == 45


def test_order_rejected_when_stock_insufficient(client, db_session):
    create_admin(db_session)
    headers = get_admin_headers(client)

    customer, product, inventory = setup_order_data(
        db_session,
        quantity=3
    )

    response = client.post(
        "/api/v1/orders/",
        json={
            "customer_id": customer.id,
            "items": [
                {
                    "product_id": product.id,
                    "quantity": 5
                }
            ]
        },
        headers=headers
    )

    assert response.status_code == 400
    assert "Insufficient stock" in response.json()["detail"]

    db_session.refresh(inventory)
    assert inventory.quantity == 3

    assert db_session.query(StockMovement).count() == 0


def test_cancel_order_restores_stock(client, db_session):
    create_admin(db_session)
    headers = get_admin_headers(client)

    customer, product, inventory = setup_order_data(db_session)

    create_response = client.post(
        "/api/v1/orders/",
        json={
            "customer_id": customer.id,
            "items": [
                {
                    "product_id": product.id,
                    "quantity": 5
                }
            ]
        },
        headers=headers
    )

    assert create_response.status_code == 201

    order_id = create_response.json()["id"]

    db_session.refresh(inventory)
    assert inventory.quantity == 45

    cancel_response = client.patch(
        f"/api/v1/orders/{order_id}/status",
        json={"status": "CANCELLED"},
        headers=headers
    )

    assert cancel_response.status_code == 200
    assert cancel_response.json()["status"] == "CANCELLED"

    db_session.refresh(inventory)
    assert inventory.quantity == 50

    movements = (
        db_session.query(StockMovement)
        .order_by(StockMovement.id)
        .all()
    )

    assert len(movements) == 2
    assert movements[0].movement_type == "OUT"
    assert movements[1].movement_type == "IN"


def test_invalid_order_status_transition(client, db_session):
    create_admin(db_session)
    headers = get_admin_headers(client)

    customer, product, inventory = setup_order_data(db_session)

    create_response = client.post(
        "/api/v1/orders/",
        json={
            "customer_id": customer.id,
            "items": [
                {
                    "product_id": product.id,
                    "quantity": 2
                }
            ]
        },
        headers=headers
    )

    order_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/orders/{order_id}/status",
        json={"status": "COMPLETED"},
        headers=headers
    )

    assert response.status_code == 400
    assert "Cannot change order status" in response.json()["detail"]

    db_session.refresh(inventory)
    assert inventory.quantity == 48


def test_get_order_by_id(client, db_session):
    create_admin(db_session)
    headers = get_admin_headers(client)
    customer, product, inventory = setup_order_data(db_session)

    create_response = client.post(
        "/api/v1/orders/",
        json={
            "customer_id": customer.id,
            "items": [{"product_id": product.id, "quantity": 2}]
        },
        headers=headers
    )

    order_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/orders/{order_id}",
        headers=headers
    )

    assert response.status_code == 200
    assert response.json()["id"] == order_id


def test_filter_orders_by_status(client, db_session):
    create_admin(db_session)
    headers = get_admin_headers(client)
    customer, product, inventory = setup_order_data(db_session)

    client.post(
        "/api/v1/orders/",
        json={
            "customer_id": customer.id,
            "items": [{"product_id": product.id, "quantity": 2}]
        },
        headers=headers
    )

    response = client.get(
        "/api/v1/orders/?status=PENDING",
        headers=headers
    )

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["orders"][0]["status"] == "PENDING"


def test_search_orders_by_customer(client, db_session):
    create_admin(db_session)
    headers = get_admin_headers(client)
    customer, product, inventory = setup_order_data(db_session)

    client.post(
        "/api/v1/orders/",
        json={
            "customer_id": customer.id,
            "items": [{"product_id": product.id, "quantity": 2}]
        },
        headers=headers
    )

    response = client.get(
        "/api/v1/orders/?search=Test Customer",
        headers=headers
    )

    assert response.status_code == 200
    assert response.json()["total"] == 1


def test_order_pagination(client, db_session):
    create_admin(db_session)
    headers = get_admin_headers(client)
    customer, product, inventory = setup_order_data(db_session)

    for _ in range(2):
        client.post(
            "/api/v1/orders/",
            json={
                "customer_id": customer.id,
                "items": [{"product_id": product.id, "quantity": 1}]
            },
            headers=headers
        )

    response = client.get(
        "/api/v1/orders/?skip=0&limit=1",
        headers=headers
    )

    assert response.status_code == 200
    assert response.json()["total"] == 2
    assert len(response.json()["orders"]) == 1


def test_invalid_order_sort_field(client, db_session):
    create_admin(db_session)
    headers = get_admin_headers(client)

    response = client.get(
        "/api/v1/orders/?sort_by=invalid",
        headers=headers
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid sorting field."


def test_invalid_order_sort_direction(client, db_session):
    create_admin(db_session)
    headers = get_admin_headers(client)

    response = client.get(
        "/api/v1/orders/?sort_order=invalid",
        headers=headers
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Sort order must be asc or desc."
