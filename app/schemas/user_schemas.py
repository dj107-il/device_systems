from datetime import datetime
from typing import Literal
from pydantic import BaseModel,ConfigDict, EmailStr, Field

# Modelo de respuesta anterior.
# Se conserva temporalmente mientras migramos las rutas y servicios.
class UserCreate(BaseModel):
    name: str = Field(min_length=3, max_length=50)
    email: EmailStr
    role: Literal["admin", "support", "user"]
    is_active: bool = True

class UserUpdate(BaseModel):
    name: str = Field(min_length=3, max_length=50)
    email: EmailStr
    role: Literal["admin", "support", "user"]
    is_active: bool

class UserPatch(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=3,
        max_length=50
    )
    email: EmailStr | None = None
    role: Literal["admin", "support", "user"] | None = None
    is_active: bool | None = None

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    role: Literal["admin", "support", "user"]
    is_active: bool
    created_at: datetime