# app/schemas/user.py

from pydantic import BaseModel, EmailStr
from datetime import datetime

from pydantic import BaseModel, EmailStr, constr

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: constr(min_length=6, max_length=72)  # ✅ bcrypt-safe



class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str
    created_at: datetime

    class Config:
        from_attributes = True
