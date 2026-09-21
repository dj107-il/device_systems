from typing import Literal
from pydantic import BaseModel, EmailStr, Field

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
    
class UserUpdate(BaseModel):
    name: str = Field(min_length=3, max_length=50)
    email: EmailStr
    role: Literal["admin", "support", "user"]
    is_active: bool
    
class UserPatch(BaseModel):
    name: str | None = Field(default=None, min_length=3, max_length=50)
    email: EmailStr | None = None 
    role: Literal["admin", "support", "user"] | None = None
    is_active: bool | None = None
    