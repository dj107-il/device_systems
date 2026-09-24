from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

LoanStatus = Literal["active", "returned", "overdue"]

class LoanCreate(BaseModel):
    user_id: int = Field(gt=0)
    device_id: int = Field(gt=0)

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "user_id": 1,
                    "device_id": 1
                }
            ]
        }
    )

class LoanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    device_id: int
    loan_date: datetime
    return_date: datetime | None
    status: LoanStatus

class LoanUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr

class LoanDeviceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    serial_number: str
    device_type: str

class LoanDetailResponse(LoanResponse):
    user: LoanUserResponse
    device: LoanDeviceResponse