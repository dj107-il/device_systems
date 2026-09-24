from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from app.database.connection import Base

def fecha_actual_utc():
    return datetime.now(timezone.utc).replace(tzinfo=None)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    name = Column(String(50), nullable=False)

    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    role = Column(String(20), nullable=False)

    is_active = Column(
        Boolean,
        default=True,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=fecha_actual_utc,
        nullable=False
    )