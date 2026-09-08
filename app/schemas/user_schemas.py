from pydantic import BaseModel, EmailStr, Field
from typing import Literal

class User(BaseModel):
    id: int
    name: str = Field(min_length=3, max_length=50)
    email: EmailStr
    role: Literal["admin", "support", "user"]
    is_active: bool
    
class UserCreate(BaseModel):
    name: str = Field(min_length=3, max_length=50)
    email: EmailStr
    role: Literal["admin", "support", "user"]
    is_active: bool
    