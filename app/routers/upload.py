from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from typing import Optional, List
import os
import uuid
from datetime import datetime
from app.utils.auth import get_current_user
from app.models.user import User
from typing import Annotated
from app.utils.robo_workflow import detect_cardamage
import base64
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.detection import Detection
from sqlalchemy import func, distinct

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
    
@router.post("/detect")
async def detect(
    current_user: Annotated[User, Depends(get_current_user)],
    front: Optional[UploadFile] = File(None),
    leftSide: Optional[UploadFile] = File(None),
    rightSide: Optional[UploadFile] = File(None),
    back: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
): 
    if not any([front, leftSide, rightSide, back]):
        raise HTTPException(status_code=400, detail="At least one image is required")
    
    # 탐지 세트 ID 생성
    detection_set_id = str(uuid.uuid4())
    
    # 날짜별 폴더 생성
    date_folder = create_date_folder()
    results = []
    
    # 각 이미지 처리
    for image, position in [(front, "front"), (leftSide, "leftSide"), (rightSide, "rightSide"), (back, "back")]:
        if not image:
            continue
            
        print(f"Processing {position} image: {image.filename}")
        print(f"Content type: {image.content_type}")
        
        # 임시 파일로 저장
        temp_path = os.path.join(date_folder, f"temp_{position}_{image.filename}")
        with open(temp_path, "wb") as buffer:
            content = await image.read()
            buffer.write(content)
        
        result = detect_cardamage(temp_path)
        
        # 임시 파일 삭제
        os.remove(temp_path)
        
        if result and len(result) > 0:
            detection_result = result[0]
            
            # base64 이미지를 파일로 저장
            base64_image = detection_result["output_image"].split(",")[1] if "," in detection_result["output_image"] else detection_result["output_image"]
            image_data = base64.b64decode(base64_image)
            
            # UUID를 사용하여 고유한 파일명 생성
            output_filename = f"{position}_{uuid.uuid4()}.jpg"
            output_path = os.path.join(date_folder, output_filename)
            
            # 이미지 파일 저장
            with open(output_path, "wb") as f:
                f.write(image_data)
            
            # DB에 저장
            detection = Detection(
                user_id=current_user.id,
                detection_set_id=detection_set_id,
                position=position,
                image_path=output_path,
                detected_at=datetime.utcnow()
            )
            db.add(detection)
            db.commit()
            db.refresh(detection)
            
            # 원본 결과에서 output_image를 저장된 파일 경로로 대체
            detection_result["output_image"] = output_path
            detection_result["position"] = position
            detection_result["detection_id"] = detection.id
            detection_result["detection_set_id"] = detection_set_id
            
            results.append(detection_result)
    
    if not results:
        return {
            "status": "success",
            "message": "No damage detected in any images",
            "data": []
        }
    
    return {
        "status": "success",
        "message": "Damage detection completed",
        "detection_set_id": detection_set_id,
        "data": results
    }

@router.get("/history")
async def get_detection_history(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    # 전체 감지 내역 조회
    subquery = db.query(
        Detection.detection_set_id,
        func.max(Detection.detected_at).label('max_detected_at')
    ).filter(
        Detection.user_id == current_user.id
    ).group_by(
        Detection.detection_set_id
    ).subquery()

    detections = db.query(
        Detection.detection_set_id,
        Detection.detected_at
    ).join(
        subquery,
        (Detection.detection_set_id == subquery.c.detection_set_id) &
        (Detection.detected_at == subquery.c.max_detected_at)
    ).order_by(
        Detection.detected_at.desc()
    ).all()
    
    history = [
        {
            "detection_set_id": detection.detection_set_id,
            "detected_at": detection.detected_at.strftime("%Y-%m-%d %H:%M:%S")
        }
        for detection in detections
    ]
    
    return {
        "status": "success",
        "data": history
    }

@router.get("/history/{detection_set_id}")
async def get_detection_details(
    detection_set_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    # 특정 detection_set_id의 이미지 정보 조회
    detections = db.query(
        Detection.position,
        Detection.image_path
    ).filter(
        Detection.user_id == current_user.id,
        Detection.detection_set_id == detection_set_id
    ).order_by(
        Detection.position
    ).all()
    
    if not detections:
        raise HTTPException(
            status_code=404,
            detail="해당 감지 내역을 찾을 수 없습니다."
        )
    
    # 결과 형식 변환
    images = [
        {
            "position": detection.position,
            "image_path": detection.image_path
        }
        for detection in detections
    ]
    
    return {
        "status": "success",
        "detection_set_id": detection_set_id,
        "data": images
    }