from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

DeviceType = Literal[
    "laptop",
    "tablet",
    "proyector",
    "camara",
    "router",
    "monitor"
]

class DeviceCreate(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    serial_number: str = Field(min_length=1, max_length=100)
    device_type: DeviceType
    brand: str | None = Field(default=None, min_length=1, max_length=50)
    is_available: bool = True

    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "examples": [
                {
                    "name": "Laptop Lenovo ThinkPad",
                    "serial_number": "LEN-2026-001",
                    "device_type": "laptop",
                    "brand": "Lenovo",
                    "is_available": True
                }
            ]
        }
    )

class DeviceUpdate(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    serial_number: str = Field(min_length=1, max_length=100)
    device_type: DeviceType
    brand: str | None = Field(min_length=1, max_length=50)
    is_available: bool

    model_config = ConfigDict(str_strip_whitespace=True)

class DevicePatch(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=3,
        max_length=100
    )

    serial_number: str | None = Field(
        default=None,
        min_length=1,
        max_length=100
    )

    device_type: DeviceType | None = None

    brand: str | None = Field(
        default=None,
        min_length=1,
        max_length=50
    )

    is_available: bool | None = None

    model_config = ConfigDict(str_strip_whitespace=True)

class DeviceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    serial_number: str
    device_type: DeviceType
    brand: str | None
    is_available: bool
    created_at: datetime