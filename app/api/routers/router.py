from fastapi import APIRouter

from app.domain.schemas.user import UserOut

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/test", response_model=UserOut)
def get_test_user():
    return {
        "telegram_id": 1234567890,
        "username": "testuser",
        "first_name": "Test",
        "last_name":"User",
    }