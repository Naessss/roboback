from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.inquiry import Inquiry
from app.schemas.inquiry import InquiryCreate
from app.models.user import User
from app.utils.auth import get_current_user
from typing import List
from app.schemas.inquiry import InquiryResponse

router = APIRouter()

@router.post("/create", status_code=status.HTTP_201_CREATED)
def create_inquiry(
    request: InquiryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    inquiry = Inquiry(
        title=request.title,
        phone=request.phone,
        wr_content=request.wr_content,
        user_id=current_user.id
    )
    db.add(inquiry)
    db.commit()
    db.refresh(inquiry)
    return {"message": "문의가 등록되었습니다."}


@router.get("/list", response_model=List[InquiryResponse])
def get_inquiry_list(db: Session = Depends(get_db)):
    return db.query(Inquiry).all()    
