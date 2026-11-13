
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import hash_password, verify_password


def register_user(db: Session, user_data: UserCreate):

    # Check whether the email already exists
    existing_user = db.query(User).filter(
        User.email == user_data.email
    ).first()

    if existing_user:
        raise ValueError("Email is already registered.")

    # Hash the user's password
    hashed_password = hash_password(user_data.password)

    # Create the new user
    new_user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        hashed_password=hashed_password,
        role="staff"
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user

    except IntegrityError:
        db.rollback()
        raise ValueError("User could not be registered.")


def authenticate_user(
    db: Session,
    email: str,
    password: str
):
    # Find user by email
    user = db.query(User).filter(
        User.email == email
    ).first()

    # Check whether user exists and is active
    if not user or not user.is_active:
        return None

    # Verify entered password
    password_is_valid = verify_password(
        password,
        user.hashed_password
    )

    if not password_is_valid:
        return None

    return user
