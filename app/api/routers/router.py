from fastapi import APIRouter

from app.api.routers.filter_router import router as filter_router
from app.api.routers.notification_router import router as notification_router
from app.api.routers.scholarship_router import router as scholarship_router
from app.api.routers.user_router import router as user_router

router = APIRouter()
router.include_router(user_router)
router.include_router(filter_router)
router.include_router(scholarship_router)
router.include_router(notification_router)