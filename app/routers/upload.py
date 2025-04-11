from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from typing import Optional
import os
import uuid
from datetime import datetime
from app.utils.auth import get_current_user
from app.models.user import User
from typing import Annotated

router = APIRouter()

# 업로드된 이미지를 저장할 기본 디렉토리
UPLOAD_DIR = "uploads"

# 날짜별 폴더 생성 함수
def create_date_folder():
    today = datetime.now()
    year = str(today.year)
    month = str(today.month).zfill(2)
    day = str(today.day).zfill(2)
    
    date_folder = os.path.join(UPLOAD_DIR, year, month, day)
    os.makedirs(date_folder, exist_ok=True)
    return date_folder

@router.post("/images")
async def upload_images(
    current_user: Annotated[User, Depends(get_current_user)],
    front: Optional[UploadFile] = File(None),
    leftSide: Optional[UploadFile] = File(None),
    rightSide: Optional[UploadFile] = File(None),
    back: Optional[UploadFile] = File(None)
):
    try:
        # 날짜별 폴더 생성
        date_folder = create_date_folder()
        
        uploaded_files = {
            "front": None,
            "leftSide": None,
            "rightSide": None,
            "back": None
        }
        
        # 각 이미지 처리 함수
        async def process_image(file: Optional[UploadFile], position: str):
            if file:
                if not file.content_type.startswith('image/'):
                    raise HTTPException(
                        status_code=400,
                        detail=f"{position} 이미지는 이미지 파일이어야 합니다."
                    )
                
                file_extension = os.path.splitext(file.filename)[1]
                unique_filename = f"{uuid.uuid4()}{file_extension}"
                file_path = os.path.join(date_folder, unique_filename)
                
                with open(file_path, "wb") as buffer:
                    content = await file.read()
                    buffer.write(content)
                
                return {
                    "original_filename": file.filename,
                    "saved_filename": unique_filename,
                    "file_path": file_path,
                    "content_type": file.content_type,
                    "size": len(content)
                }
            return None
        
        # 각 위치별 이미지 처리
        uploaded_files["front"] = await process_image(front, "정면")
        uploaded_files["leftSide"] = await process_image(leftSide, "왼쪽")
        uploaded_files["rightSide"] = await process_image(rightSide, "오른쪽")
        uploaded_files["back"] = await process_image(back, "후면")
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "이미지 업로드 성공",
                "uploaded_files": uploaded_files
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"이미지 업로드 중 오류 발생: {str(e)}"
        ) 