# C:\pro\main.py (수정 제안)

# ================== 필요한 라이브러리 임포트 ==================
from fastapi import FastAPI, Request, Depends, HTTPException
# PlainTextResponse는 이제 홈 라우트에서 사용하지 않으므로 제거해도 무방합니다. (필요시 유지)
from fastapi.responses import HTMLResponse, RedirectResponse #, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import os

# app 폴더 내 모듈 임포트
from app import crud, models, schemas, database
# from app.database import engine # engine은 startup 이벤트에서 사용
from app.routers import hunting_sessions, jjul_sessions, meso_sales, statistics

# FastAPI 앱 인스턴스 생성
app = FastAPI(
    title="메이플스토리 수익 기록 웹 프로그램",
    description="메이플스토리 활동으로 얻는 수익을 기록하고 통계를 제공하는 웹 애플리케이션",
    version="1.0.0"
)

# --- FastAPI 시작/종료 이벤트 핸들러 ---
@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 실행됩니다."""
    try:
        print("데이터베이스 테이블 생성 시도 (startup 이벤트)...")
        # models.Base.metadata.drop_all(bind=database.engine) # 필요하다면 기존 테이블 삭제 후 재생성
        models.Base.metadata.create_all(bind=database.engine)
        print("데이터베이스 테이블 확인/생성 완료 (startup 이벤트).")
    except Exception as e:
        print(f"데이터베이스 테이블 생성 중 오류 발생 (startup 이벤트): {e}")

# @app.on_event("shutdown")
# async def shutdown_event():
#     """애플리케이션 종료 시 실행됩니다."""
#     print("애플리케이션 종료")
# --- FastAPI 시작/종료 이벤트 핸들러 끝 ---


# --- 정적 파일 마운트 ---
app.mount("/static", StaticFiles(directory="static"), name="static")
# --- 정적 파일 마운트 끝 ---

# --- Jinja2 템플릿 설정 ---
templates = Jinja2Templates(directory="templates")
# --- Jinja2 템플릿 설정 끝 ---

# --- 데이터베이스 의존성 함수 ---
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()
# --- 데이터베이스 의존성 함수 끝 ---


# ================== API 라우터 등록 ==================
# 각 라우터 모듈의 경로들을 특정 prefix 뒤에 연결합니다.
# (경로는 일단 이전 상태 유지)
app.include_router(
    hunting_sessions.router,
    prefix="/api/hunting-times",
    tags=["Hunting Times API"]
)
app.include_router(
    jjul_sessions.router,
    prefix="/api/jjul-times",
    tags=["Jjul Times API"]
)
app.include_router(
    meso_sales.router,
    prefix="/api/meso-sales",
    tags=["Meso Sales API"]
)
app.include_router(
    statistics.router,
    prefix="/api/statistics",
    tags=["Statistics API"]
)
# ================== API 라우터 등록 끝 ==================


# ================== UI 페이지 라우트 정의 ==================
# 웹 브라우저에서 접속하는 각 페이지 경로 처리

# === 홈 라우트 수정 ===
@app.get("/", response_class=HTMLResponse, name="read_home", tags=["UI Pages"]) # response_class를 HTMLResponse로 수정!
async def read_home(request: Request):
    """메인 홈 페이지를 반환합니다."""
    # 이제 정상적으로 TemplateResponse 사용
    return templates.TemplateResponse("home.html", {"request": request})

# === 나머지 UI 라우트는 이전과 동일하게 유지 ===
@app.get("/meso-sales", response_class=HTMLResponse, name="meso_sales_page", tags=["UI Pages"])
async def meso_sales_page(request: Request):
    """메소 판매 기록 페이지를 반환합니다."""
    return templates.TemplateResponse("list_and_add_meso_sales.html", {"request": request})

@app.get("/hunting-times", response_class=HTMLResponse, name="hunting_times_page", tags=["UI Pages"])
async def hunting_times_page(request: Request):
    """사냥 기록 페이지를 반환합니다."""
    return templates.TemplateResponse("list_and_add_hunting_sessions.html", {"request": request})

@app.get("/jjul-times", response_class=HTMLResponse, name="jjul_times_page", tags=["UI Pages"])
async def jjul_times_page(request: Request):
    """쩔 기록 페이지를 반환합니다."""
    return templates.TemplateResponse("list_and_add_jjul_sessions.html", {"request": request})

@app.get("/statistics/daily", response_class=HTMLResponse, name="statistics_daily_page", tags=["UI Pages"])
async def statistics_daily_page(request: Request):
    """일별 통계 페이지를 반환합니다."""
    return templates.TemplateResponse("statistics_daily.html", {"request": request})

@app.get("/statistics/map", response_class=HTMLResponse, name="statistics_map_page", tags=["UI Pages"])
async def statistics_map_page(request: Request):
    """맵별 통계 페이지를 반환합니다."""
    return templates.TemplateResponse("statistics_map.html", {"request": request})

@app.get("/statistics/weekday", response_class=HTMLResponse, name="statistics_weekday_page", tags=["UI Pages"])
async def statistics_weekday_page(request: Request):
    """요일별 통계 페이지를 반환합니다."""
    return templates.TemplateResponse("statistics_weekday.html", {"request": request})

@app.get("/statistics/experience", response_class=HTMLResponse, name="read_experience_statistics_page", tags=["UI Pages"])
async def read_experience_statistics_page(request: Request):
    """경험치 통계 페이지를 렌더링합니다."""
    return templates.TemplateResponse("statistics_experience.html", {"request": request})

# ================== UI 페이지 라우트 정의 끝 ==================

# (서버 실행은 터미널에서 'uvicorn main:app --reload' 사용 권장)