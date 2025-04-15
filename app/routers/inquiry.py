from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.inquiry import Inquiry
from app.schemas.inquiry import InquiryResponse
from app.utils.auth import get_current_user

router = APIRouter()

# 게시판 상세페이지 

@router.get("/inquiry/{inquiry_id}", response_model=InquiryResponse)
def get_inquiry_detail(inquiry_id: int, db: Session = Depends(get_db)):
    inquiry = db.query(Inquiry).filter(Inquiry.id == inquiry_id).first()
    if not inquiry:
        raise HTTPException(status_code=404, detail="문의 내용을 찾을 수 없습니다.")
    return inquiry

# 게시판 삭제 
@router.delete("/inquiry/{inquiry_id}", status_code=204)
def delete_inquiry(
    inquiry_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    inquiry = db.query(Inquiry).filter(Inquiry.id == inquiry_id).first()
    if not inquiry:
        raise HTTPException(status_code=404, detail="문의 내역을 찾을 수 없습니다.")
    if inquiry.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="삭제 권한이 없습니다.")

    db.delete(inquiry)
    db.commit()   