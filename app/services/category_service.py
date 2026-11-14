
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


def create_category(db: Session, category_data: CategoryCreate):
    existing_category = (
        db.query(Category)
        .filter(Category.name == category_data.name)
        .first()
    )

    if existing_category:
        raise ValueError("Category name already exists.")

    new_category = Category(
        name=category_data.name,
        description=category_data.description
    )

    try:
        db.add(new_category)
        db.commit()
        db.refresh(new_category)
        return new_category

    except IntegrityError:
        db.rollback()
        raise ValueError("Category name already exists.")


def get_all_categories(db: Session):
    return (
        db.query(Category)
        .filter(Category.is_active == True)
        .order_by(Category.id.desc())
        .all()
    )


def get_category_by_id(db: Session, category_id: int):
    return (
        db.query(Category)
        .filter(
            Category.id == category_id,
            Category.is_active == True
        )
        .first()
    )


def update_category(
    db: Session,
    category_id: int,
    category_data: CategoryUpdate
):
    category = get_category_by_id(db, category_id)

    if category is None:
        return None

    update_data = category_data.model_dump(exclude_unset=True)

    if "name" in update_data and update_data["name"] is not None:
        existing_category = (
            db.query(Category)
            .filter(
                Category.name == update_data["name"],
                Category.id != category_id
            )
            .first()
        )

        if existing_category:
            raise ValueError("Category name already exists.")

    for field, value in update_data.items():
        setattr(category, field, value)

    try:
        db.commit()
        db.refresh(category)
        return category

    except IntegrityError:
        db.rollback()
        raise ValueError("Category name already exists.")


def deactivate_category(db: Session, category_id: int):
    category = get_category_by_id(db, category_id)

    if category is None:
        return None

    category.is_active = False

    db.commit()
    db.refresh(category)

    return category
