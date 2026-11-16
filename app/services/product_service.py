
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from decimal import Decimal

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
    


def get_all_products(
    db: Session,
    search: str | None = None,
    category_id: int | None = None,
    min_price: Decimal | None = None,
    max_price: Decimal | None = None,
    skip: int = 0,
    limit: int = 10,
    sort_by: str = "id",
    sort_order: str = "desc"
):
    query = db.query(Product).filter(
        Product.is_active.is_(True)
    )

    # Search by product name or SKU.
    if search:
        search_term = f"%{search.strip()}%"

        query = query.filter(
            Product.name.ilike(search_term) |
            Product.sku.ilike(search_term)
        )

    # Filter by category.
    if category_id is not None:
        query = query.filter(
            Product.category_id == category_id
        )

    # Filter by minimum price.
    if min_price is not None:
        query = query.filter(
            Product.price >= min_price
        )

    # Filter by maximum price.
    if max_price is not None:
        query = query.filter(
            Product.price <= max_price
        )

    # Sorting.
    sort_columns = {
        "id": Product.id,
        "name": Product.name,
        "price": Product.price
    }

    sort_column = sort_columns.get(sort_by)

    if sort_column is None:
        raise ValueError("Invalid sorting field.")

    if sort_order == "asc":
        query = query.order_by(sort_column.asc())
    elif sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        raise ValueError("Sort order must be asc or desc.")

    # Pagination.
    return query.offset(skip).limit(limit).all()


def count_products(
    db: Session,
    search: str | None = None,
    category_id: int | None = None,
    min_price: Decimal | None = None,
    max_price: Decimal | None = None
):
    query = db.query(Product).filter(
        Product.is_active.is_(True)
    )

    if search:
        search_term = f"%{search.strip()}%"

        query = query.filter(
            Product.name.ilike(search_term) |
            Product.sku.ilike(search_term)
        )

    if category_id is not None:
        query = query.filter(
            Product.category_id == category_id
        )

    if min_price is not None:
        query = query.filter(Product.price >= min_price)

    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    return query.count()



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