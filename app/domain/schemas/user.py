from pydantic import BaseModel

class UserOut(BaseModel):
    telegram_id:int
    username:str
    first_name:str
    last_name:str
    