from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.connection import Base

class Inquiry(Base):  
    __tablename__ = "inquiry"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=False)
    wr_content = Column(String(1000), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="inquiries")
