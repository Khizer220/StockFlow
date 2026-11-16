
from app.models.category import Category
from app.models.user import User
from app.core.security import hash_password


def create_user(db_session, role="admin"):
    user = User(
        full_name="Test User",
        email=f"{role}@stockflow.com",
        hashed_password=hash_password("TestPassword123"),
        role=role,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def get_auth_headers(client, email):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": "TestPassword123"
        }
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


def test_create_category(client, db_session):
    create_user(db_session)
    headers = get_auth_headers(client, "admin@stockflow.com")

    response = client.post(
        "/api/v1/categories/",
        json={
            "name": "Electronics",
            "description": "Electronic products"
        },
        headers=headers
    )

    assert response.status_code == 201
    assert response.json()["name"] == "Electronics"
    assert response.json()["description"] == "Electronic products"
    assert response.json()["is_active"] is True


def test_get_all_categories(client, db_session):
    create_user(db_session)
    headers = get_auth_headers(client, "admin@stockflow.com")

    db_session.add_all([
        Category(name="Electronics", description="Electronic items"),
        Category(name="Furniture", description="Furniture items")
    ])
    db_session.commit()

    response = client.get(
        "/api/v1/categories/",
        headers=headers
    )

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_category_by_id(client, db_session):
    create_user(db_session)
    headers = get_auth_headers(client, "admin@stockflow.com")

    category = Category(
        name="Electronics",
        description="Electronic items"
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)

    response = client.get(
        f"/api/v1/categories/{category.id}",
        headers=headers
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Electronics"


def test_update_category(client, db_session):
    create_user(db_session)
    headers = get_auth_headers(client, "admin@stockflow.com")

    category = Category(name="Electronics")
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)

    response = client.put(
        f"/api/v1/categories/{category.id}",
        json={"name": "Electrical Appliances"},
        headers=headers
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Electrical Appliances"


def test_duplicate_category_rejected(client, db_session):
    create_user(db_session)
    headers = get_auth_headers(client, "admin@stockflow.com")

    db_session.add(Category(name="Electronics"))
    db_session.commit()

    response = client.post(
        "/api/v1/categories/",
        json={"name": "Electronics"},
        headers=headers
    )

    assert response.status_code == 409


def test_deactivate_category(client, db_session):
    create_user(db_session)
    headers = get_auth_headers(client, "admin@stockflow.com")

    category = Category(name="Electronics")
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)

    response = client.delete(
        f"/api/v1/categories/{category.id}",
        headers=headers
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is False

    get_response = client.get(
        f"/api/v1/categories/{category.id}",
        headers=headers
    )

    assert get_response.status_code == 404


def test_staff_cannot_create_category(client, db_session):
    create_user(db_session, role="staff")
    headers = get_auth_headers(client, "staff@stockflow.com")

    response = client.post(
        "/api/v1/categories/",
        json={"name": "Electronics"},
        headers=headers
    )

    assert response.status_code == 403
