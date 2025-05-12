# C:\pro\app\routers\hunting_sessions.py (전체 수정본)

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import crud, schemas, models # 우리 앱의 모듈들
from app.database import SessionLocal, get_db # ✨ get_db 직접 import 또는 database.get_db 사용 ✨

router = APIRouter(
    # prefix="/hunting-sessions", # 이 prefix는 main.py에서 /api/hunting-times 로 이미 적용됨
    tags=["Hunting Sessions API"],
)

# 데이터베이스 세션 의존성 함수 (database.py의 get_db 사용)
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# --- API 엔드포인트 정의 ---

# 새로운 사냥 세션 기록 생성 API
@router.post("/", response_model=schemas.HuntingSession, status_code=status.HTTP_201_CREATED) # 경로를 "/"로 변경 (prefix는 main.py에서)
async def create_new_hunting_session(
    hunting_session_data: schemas.HuntingSessionCreate,
    db: Session = Depends(get_db) # ✨ database.get_db 또는 이 파일 내 get_db 사용 ✨
):
    try:
        # crud.create_hunting_session_log -> crud.create_hunting_session 으로 함수명 변경되었을 수 있음
        created_session = crud.create_hunting_session(db=db, session=hunting_session_data) # 파라미터명 session으로 변경
        return created_session
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        print(f"Error creating hunting session: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="사냥 세션 기록 생성 중 내부 서버 오류가 발생했습니다.")


# 모든 사냥 세션 기록 조회 API
@router.get("/", response_model=List[schemas.HuntingSession]) # 경로를 "/"로 변경
async def read_all_hunting_sessions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db) # ✨ database.get_db 또는 이 파일 내 get_db 사용 ✨
):
    # crud.get_hunting_session_logs -> crud.get_hunting_sessions 로 함수명 변경되었을 수 있음
    sessions = crud.get_hunting_sessions(db=db, skip=skip, limit=limit) # 함수명 변경
    return sessions


# 특정 ID의 사냥 세션 기록 조회 API
@router.get("/{session_id}", response_model=schemas.HuntingSession) # 파라미터명 session_id로 통일
async def read_single_hunting_session(session_id: int, db: Session = Depends(get_db)): # ✨ database.get_db 또는 이 파일 내 get_db 사용 ✨
    # crud.get_hunting_session_log -> crud.get_hunting_session 으로 함수명 변경되었을 수 있음
    db_session = crud.get_hunting_session(db=db, log_id=session_id) # 파라미터명 log_id로 변경
    if db_session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="해당 ID의 사냥 세션 기록을 찾을 수 없습니다.")
    return db_session