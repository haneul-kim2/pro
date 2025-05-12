# C:\pro\app\routers\jjul_sessions.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List # Python 3.9 이상에서는 list 소문자 가능

from app import crud, schemas, models # 우리 앱의 모듈들
from app.database import SessionLocal # DB 세션 생성용

router = APIRouter(
    prefix="/jjul-sessions",   # 이 라우터의 모든 경로는 /jjul-sessions 로 시작
    tags=["Jjul Sessions"],    # API 문서에서 "Jjul Sessions" 태그로 묶임
)

# 데이터베이스 세션 의존성 함수 (공통 사용 가능)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- API 엔드포인트 정의 ---

# 새로운 쩔 세션 기록 생성 API
@router.post("/", response_model=schemas.JjulSession, status_code=status.HTTP_201_CREATED)
async def create_new_jjul_session(
    jjul_session_data: schemas.JjulSessionCreate, # 요청 본문은 JjulSessionCreate 스키마
    db: Session = Depends(get_db)
):
    """
    새로운 쩔 세션 기록을 생성합니다.
    - `jjul_session_data`에는 쩔 기본 정보와 함께,
    - `rare_items` (고가 아이템 목록)
    - `consumable_items` (소모/획득 아이템 목록)
    을 포함하여 요청할 수 있습니다. 서버에서 수익을 계산하여 저장합니다.
    """
    try:
        created_session = crud.create_jjul_session_log(db=db, jjul_session=jjul_session_data)
        return created_session
    except ValueError as ve: # crud 함수에서 발생 가능한 값 관련 오류 (예: 시간 형식 등)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        print(f"Error creating jjul session: {e}") # 서버 로그에 오류 출력
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="쩔 세션 기록 생성 중 내부 서버 오류가 발생했습니다.")

# 모든 쩔 세션 기록 조회 API
@router.get("/", response_model=List[schemas.JjulSession])
async def read_all_jjul_sessions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    모든 쩔 세션 기록을 조회합니다. (최근 기록부터)
    `skip`과 `limit` 쿼리 파라미터를 사용하여 페이지네이션을 할 수 있습니다.
    """
    sessions = crud.get_jjul_session_logs(db=db, skip=skip, limit=limit)
    return sessions

# 특정 ID의 쩔 세션 기록 조회 API
@router.get("/{session_id}", response_model=schemas.JjulSession)
async def read_single_jjul_session(session_id: int, db: Session = Depends(get_db)):
    """
    지정된 ID의 쩔 세션 기록을 상세 조회합니다.
    관련된 아이템 정보도 함께 반환됩니다.
    """
    db_session = crud.get_jjul_session_log(db, jjul_session_log_id=session_id)
    if db_session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="해당 ID의 쩔 세션 기록을 찾을 수 없습니다.")
    return db_session

# (향후 update, delete API 엔드포인트 추가 예정)