from pydantic import BaseModel


class ApiError(BaseModel):
    detail: str
    code: str


class MessageOut(BaseModel):
    message: str
