from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# SQLite 데이터베이스 파일의 경로 및 이름 설정
# 프로젝트 최상위 폴더에 'maple_data.db' 라는 이름으로 생성됩니다.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # 프로젝트 루트 디렉토리
SQLALCHEMY_DATABASE_URL = "sqlite:///" + os.path.join(BASE_DIR, "maple_data.db")
# print(f"Database URL: {SQLALCHEMY_DATABASE_URL}") # 경로 확인용 (필요시 주석 해제)

# SQLAlchemy 엔진 생성
# connect_args는 SQLite를 사용할 때만 필요합니다 (thread 문제 방지).
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 데이터베이스 세션 생성을 위한 SessionLocal 클래스
# autocommit=False: 자동으로 커밋하지 않음 (명시적으로 커밋 필요)
# autoflush=False: 자동으로 flush하지 않음 (명시적으로 flush 필요)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 데이터베이스 모델 클래스들이 상속받을 Base 클래스
Base = declarative_base()

# 데이터베이스 세션을 가져오는 함수 (의존성 주입용)
def get_db():
    db = SessionLocal()
    try:
        yield db  # db 세션 제공
    finally:
        db.close() # 사용 후 세션 닫기