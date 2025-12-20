from fastapi import APIRouter

from .operations import router as operations_router
from .todos import router as todos_router

router = APIRouter()
router.include_router(todos_router, prefix="/todos")
router.include_router(operations_router, prefix="/operations")
