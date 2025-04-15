from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, upload, inquirycreate, inquiry


app = FastAPI(title="Robo Backend API")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(upload.router, prefix="/api/upload", tags=["upload"])
app.include_router(inquirycreate.router, prefix="/api/inquirycreate", tags=["inquiryCreate"])
app.include_router(inquiry.router, prefix="/api", tags=["inquiry"])

@app.get("/")
async def root():
    return {"message": "Welcome to Robo Backend API"} 