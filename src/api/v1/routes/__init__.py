from fastapi import APIRouter

from src.api.v1.routes.mortgage import router as mortgage_router

v1_router = APIRouter()
v1_router.include_router(mortgage_router)
