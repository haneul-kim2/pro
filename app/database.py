import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, MappedAsDataclass # 필요시 Dataclass 관련 임포트
from sqlalchemy.pool import NullPool # Render에서 권장될 수 있는 NullPool

# Render 배포 환경에서는 DATABASE_URL 환경 변수를 사용합니다.
# 이 환경 변수는 Render 대시보드에서 설정하며, PostgreSQL 접속 정보를 담습니다.
# 예: postgresql://user:password@host:port/database
SQLALCHEMY_DATABASE_URL_ENV = os.getenv("DATABASE_URL")

if SQLALCHEMY_DATABASE_URL_ENV:
    # Render 환경 (PostgreSQL 사용)
    # Render의 PostgreSQL은 SSL을 요구할 수 있으므로, ?sslmode=require 등을 추가해야 할 수 있습니다.
    # DB 접속 문자열은 Render에서 제공하는 'Internal Connection String'을 그대로 사용하면 됩니다.
    # 예: postgresql://유저이름:비밀번호@호스트주소:포트번호/데이터베이스이름
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL_ENV
    # Render와 같은 PaaS 환경에서는 NullPool을 사용하는 것이 권장되기도 합니다.
    # engine = create_engine(SQLALCHEMY_DATABASE_URL, poolclass=NullPool)
    engine = create_engine(SQLALCHEMY_DATABASE_URL) # 기본 풀링으로 시작
else:
    # 로컬 개발 환경 (SQLite 사용)
    # 이 database.py 파일이 있는 디렉토리: /app/
    current_file_dir = os.path.dirname(os.path.abspath(__file__))
    # 프로젝트 루트 디렉토리는 app 폴더의 부모 폴더입니다.
    project_root_dir = os.path.abspath(os.path.join(current_file_dir, os.pardir))
    SQLALCHEMY_DATABASE_URL = "sqlite:///" + os.path.join(project_root_dir, "maple_data.db")
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )

print(f"[DATABASE] Using database URL: {SQLALCHEMY_DATABASE_URL}") # 경로 확인용

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()