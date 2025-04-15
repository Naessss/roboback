from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserInInquiry(BaseModel):
    email: str

    class Config:
        from_attributes = True  


class InquiryCreate(BaseModel):
    title: str
    phone: str
    wr_content: str


class InquiryResponse(BaseModel):
    id: int
    title: str
    phone: str
    wr_content: str
    created_at: datetime
    user_id: Optional[int]
    user: Optional[UserInInquiry]

    class Config:
        orm_mode = True
