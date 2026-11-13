
from getpass import getpass

from app.database.session import SessionLocal
from app.models.user import User
from app.core.security import hash_password


def create_admin():
    db = SessionLocal()

    try:
        full_name = input("Enter admin name: ").strip()
        email = input("Enter admin email: ").strip().lower()
        password = getpass("Enter admin password: ")

        if len(password.encode("utf-8")) > 72:
            print("Password must not exceed 72 UTF-8 bytes.")
            return

        if len(password) < 8:
            print("Password must contain at least 8 characters.")
            return

        existing_user = db.query(User).filter(
            User.email == email
        ).first()

        if existing_user:
            print("A user with this email already exists.")
            return

        admin = User(
            full_name=full_name,
            email=email,
            hashed_password=hash_password(password),
            role="admin",
            is_active=True
        )

        db.add(admin)
        db.commit()

        print("Admin account created successfully!")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    create_admin()
