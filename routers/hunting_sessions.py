# C:\pro\app\routers\hunting_sessions.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List # Python 3.9 이상에서는 list 소문자 가능

from app import crud, schemas, models # 우리 앱의 모듈들
from app.database import SessionLocal # DB 세션 생성용

router = APIRouter(
    prefix="/hunting-sessions", # 이 라우터의 모든 경로는 /hunting-sessions 로 시작
    tags=["Hunting Sessions"],  # API 문서에서 "Hunting Sessions" 태그로 묶임
)

# 데이터베이스 세션 의존성 함수 (meso_sales.py의 get_db와 동일)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- API 엔드포인트 정의 ---

# 새로운 사냥 세션 기록 생성 API
@router.post("/", response_model=schemas.HuntingSession, status_code=status.HTTP_201_CREATED)
async def create_new_hunting_session(
    hunting_session_data: schemas.HuntingSessionCreate, # 요청 본문은 HuntingSessionCreate 스키마
    db: Session = Depends(get_db)
):
    """
    새로운 사냥 세션 기록을 생성합니다.
    - `hunting_session_data`에는 사냥 기본 정보와 함께,
    - `rare_items` (고가 아이템 목록)
    - `consumable_items` (소모/획득 아이템 목록)
    을 포함하여 요청할 수 있습니다. 서버에서 수익 및 경험치를 계산하여 저장합니다.
    """
    try:
        created_session = crud.create_hunting_session_log(db=db, hunting_session=hunting_session_data)
        return created_session
    except ValueError as ve: # crud 함수에서 시간 형식 오류 등 발생 시
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        # 실제 운영에서는 더 구체적인 오류 로깅 및 처리가 필요
        print(f"Error creating hunting session: {e}") # 서버 로그에 오류 출력
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="사냥 세션 기록 생성 중 내부 서버 오류가 발생했습니다.")


# 모든 사냥 세션 기록 조회 API
@router.get("/", response_model=List[schemas.HuntingSession])
async def read_all_hunting_sessions(
    skip: int = 0,
    limit: int = 100, # 기본적으로 최근 100개
    db: Session = Depends(get_db)
):
    """
    모든 사냥 세션 기록을 조회합니다. (최근 기록부터)
    `skip`과 `limit` 쿼리 파라미터를 사용하여 페이지네이션을 할 수 있습니다.
    """
    sessions = crud.get_hunting_session_logs(db=db, skip=skip, limit=limit)
    return sessions


# 특정 ID의 사냥 세션 기록 조회 API
@router.get("/{session_id}", response_model=schemas.HuntingSession)
async def read_single_hunting_session(session_id: int, db: Session = Depends(get_db)):
    """
    지정된 ID의 사냥 세션 기록을 상세 조회합니다.
    관련된 고가 아이템 및 소모/획득 아이템 정보도 함께 반환됩니다.
    """
    db_session = crud.get_hunting_session_log(db, hunting_session_log_id=session_id)
    if db_session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="해당 ID의 사냥 세션 기록을 찾을 수 없습니다.")
    return db_session

# (향후 update, delete API 엔드포인트 추가 예정)