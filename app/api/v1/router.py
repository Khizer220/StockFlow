
from fastapi import APIRouter

from app.api.v1.endpoints import products, auth


api_router = APIRouter()

api_router.include_router(products.router)
api_router.include_router(auth.router)
