# C:\pro\app\routers\jjul_sessions.py (수정 후 제안)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import crud, schemas, models # ✨ 상위 폴더 참조로 변경 ✨
from ..database import get_db # ✨ database 모듈에서 get_db 직접 import ✨

# ================== ✨ 라우터 객체 생성 (prefix 없이) ✨ ==================
router = APIRouter(
    # prefix는 main.py에서 /api/jjul-times 로 이미 적용됨
    tags=["Jjul Sessions API"] # 태그는 여기서 정의 가능
)
# =======================================================================

@router.post("/", response_model=schemas.JjulSession, status_code=status.HTTP_201_CREATED)
async def create_new_jjul_session(
    jjul_session_data: schemas.JjulSessionCreate,
    db: Session = Depends(get_db)
):
    try:
        # crud.create_jjul_session 함수 사용 (crud.py 함수명 확인 필요)
        created_session = crud.create_jjul_session(db=db, session=jjul_session_data)
        return created_session
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        print(f"Error creating jjul session: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="쩔 세션 기록 생성 중 내부 서버 오류 발생")

@router.get("/", response_model=List[schemas.JjulSession])
async def read_all_jjul_sessions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    # crud.get_jjul_sessions 함수 사용 (crud.py 함수명 확인 필요)
    sessions = crud.get_jjul_sessions(db=db, skip=skip, limit=limit)
    return sessions

@router.get("/{session_id}", response_model=schemas.JjulSession)
async def read_single_jjul_session(session_id: int, db: Session = Depends(get_db)):
    # crud.get_jjul_session 함수 사용 (crud.py 함수명 확인 필요)
    db_session = crud.get_jjul_session(db=db, log_id=session_id) # crud 함수 파라미터명 확인
    if db_session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="해당 ID의 쩔 세션 기록을 찾을 수 없습니다.")
    return db_session