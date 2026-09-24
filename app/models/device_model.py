from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.database.connection import Base


def fecha_actual_utc():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)

    serial_number = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    device_type = Column(String(30), nullable=False)
    brand = Column(String(50), nullable=True)

    is_available = Column(
        Boolean,
        default=True,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=fecha_actual_utc,
        nullable=False
    )

    loans = relationship(
        "Loan",
        back_populates="device",
        passive_deletes="all"
    )