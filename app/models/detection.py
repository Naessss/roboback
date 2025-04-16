from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.connection import Base
from datetime import datetime
import uuid

class Detection(Base):
    __tablename__ = "detections"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    detection_set_id = Column(String(36), index=True)  # UUID를 문자열로 저장
    position = Column(String(50))  # front, leftSide, rightSide, back
    image_path = Column(String(255))
    detected_at = Column(DateTime, default=datetime.utcnow)
    
    # 사용자와의 관계
    user = relationship("User", back_populates="detections") 