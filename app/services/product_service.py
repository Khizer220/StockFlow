
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


def create_product(db: Session, product_data: ProductCreate):
    # Check whether the SKU already exists
    existing_product = (
        db.query(Product)
        .filter(Product.sku == product_data.sku)
        .first()
    )

    if existing_product:
        raise ValueError("A product with this SKU already exists.")

    # Convert Pydantic data into a SQLAlchemy model
    new_product = Product(**product_data.model_dump())

    try:
        db.add(new_product)
        db.commit()
        db.refresh(new_product)

        return new_product

    except IntegrityError:
        db.rollback()
        raise ValueError("Product could not be created. Check the SKU.")
    

def get_all_products(db: Session):
    return db.query(Product).filter(
        Product.is_active.is_(True)
    ).all()

def get_product_by_id(db: Session, product_id: int):
    return db.query(Product).filter(
        Product.id == product_id,
        Product.is_active.is_(True)
    ).first()
    

def update_product(
    db: Session,
    product_id: int,
    product_data: ProductUpdate
):
    product = db.query(Product).filter(
    Product.id == product_id,
    Product.is_active.is_(True)
    ).first()

    if product is None:
        return None

    # Check whether another product uses this SKU
    existing_product = db.query(Product).filter(
        Product.sku == product_data.sku,
        Product.id != product_id
    ).first()

    if existing_product:
        raise ValueError("This SKU is already used by another product.")

    # Update product fields
    for field, value in product_data.model_dump().items():
        setattr(product, field, value)

    try:
        db.commit()
        db.refresh(product)
        return product

    except IntegrityError:
        db.rollback()
        raise ValueError("Product could not be updated.")

def delete_product(db: Session, product_id: int):
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.is_active.is_(True)
    ).first()

    if product is None:
        return None

    product.is_active = False

    db.commit()
    db.refresh(product)

    return product