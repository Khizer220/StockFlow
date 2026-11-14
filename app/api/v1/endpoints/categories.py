
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.core.dependencies import get_current_user
from app.core.permissions import require_admin

from app.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse
)

from app.services.category_service import (
    create_category,
    get_all_categories,
    get_category_by_id,
    update_category,
    deactivate_category
)


router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
    dependencies=[Depends(get_current_user)]
)


@router.post(
    "/",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED
)
def create_category_endpoint(
    category_data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    try:
        return create_category(db, category_data)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


@router.get("/", response_model=list[CategoryResponse])
def get_categories_endpoint(db: Session = Depends(get_db)):
    return get_all_categories(db)


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category_endpoint(
    category_id: int,
    db: Session = Depends(get_db)
):
    category = get_category_by_id(db, category_id)

    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    return category


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category_endpoint(
    category_id: int,
    category_data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    try:
        category = update_category(db, category_id, category_data)

        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )

        return category

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


@router.delete("/{category_id}")
def delete_category_endpoint(
    category_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    category = deactivate_category(db, category_id)

    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    return {
        "message": "Category deactivated successfully",
        "category_id": category_id,
        "is_active": category.is_active
    }

