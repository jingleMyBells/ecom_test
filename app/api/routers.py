from fastapi import APIRouter

from app.api.template import router


main_router = APIRouter()
main_router.include_router(
    router,
    tags=['Form Checker'],
)
