
from app.models.user import User
from app.core.security import hash_password


def create_admin(db_session):
    admin = User(
        full_name="Test Admin",
        email="admin.suppliers@test.com",
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
            "email": "admin.suppliers@test.com",
            "password": "AdminPass123"
        }
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_supplier(client, db_session):
    create_admin(db_session)
    headers = get_admin_headers(client)

    response = client.post(
        "/api/v1/suppliers/",
        json={
            "name": "ABC Suppliers",
            "email": "abc.suppliers@test.com",
            "phone": "9876543210",
            "address": "Bengaluru"
        },
        headers=headers
    )

    assert response.status_code == 201
    assert response.json()["name"] == "ABC Suppliers"
    assert response.json()["email"] == "abc.suppliers@test.com"
    assert response.json()["is_active"] is True


def test_get_all_suppliers(client, db_session):
    create_admin(db_session)
    headers = get_admin_headers(client)

    client.post(
        "/api/v1/suppliers/",
        json={"name": "ABC Suppliers"},
        headers=headers
    )

    response = client.get("/api/v1/suppliers/", headers=headers)

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_supplier_by_id(client, db_session):
    create_admin(db_session)
    headers = get_admin_headers(client)

    create_response = client.post(
        "/api/v1/suppliers/",
        json={"name": "ABC Suppliers"},
        headers=headers
    )
    supplier_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/suppliers/{supplier_id}",
        headers=headers
    )

    assert response.status_code == 200
    assert response.json()["id"] == supplier_id


def test_update_supplier(client, db_session):
    create_admin(db_session)
    headers = get_admin_headers(client)

    create_response = client.post(
        "/api/v1/suppliers/",
        json={"name": "ABC Suppliers"},
        headers=headers
    )
    supplier_id = create_response.json()["id"]

    response = client.put(
        f"/api/v1/suppliers/{supplier_id}",
        json={"name": "Updated Suppliers"},
        headers=headers
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Updated Suppliers"


def test_delete_supplier(client, db_session):
    create_admin(db_session)
    headers = get_admin_headers(client)

    create_response = client.post(
        "/api/v1/suppliers/",
        json={"name": "ABC Suppliers"},
        headers=headers
    )
    supplier_id = create_response.json()["id"]

    response = client.delete(
        f"/api/v1/suppliers/{supplier_id}",
        headers=headers
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is False

    get_response = client.get(
        f"/api/v1/suppliers/{supplier_id}",
        headers=headers
    )

    assert get_response.status_code == 404


def test_supplier_creation_requires_admin(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Staff User",
            "email": "staff.suppliers@test.com",
            "password": "StaffPass123"
        }
    )

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "staff.suppliers@test.com",
            "password": "StaffPass123"
        }
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(
        "/api/v1/suppliers/",
        json={"name": "Unauthorized Supplier"},
        headers=headers
    )

    assert response.status_code == 403
