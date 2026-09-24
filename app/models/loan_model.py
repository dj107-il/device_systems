from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database.connection import Base

def fecha_actual_utc():
    return datetime.now(timezone.utc).replace(tzinfo=None)

class Loan(Base):
    __tablename__ = "loans"
    
    id = Column(Integer, primary_key=True)
    
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False, 
        index=True
    )
    
    device_id = Column(
        Integer, 
        ForeignKey("devices.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    
    loan_date = Column(
        DateTime, 
        default=fecha_actual_utc,
        nullable=False
    )
    
    return_date = Column(DateTime, nullable=True)
    
    status = Column(
        String(20),
        default="active",
        nullable=False
    )
    
    user = relationship("User", back_populates="loans")
    device = relationship("Device", back_populates="loans")