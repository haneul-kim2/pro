# C:\pro\main.py (파일명 변경 없이 API 경로 매핑 수정)

import uvicorn
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app import models, schemas, crud, database
# 라우터 임포트는 원래대로 _sessions 사용
from app.routers import hunting_sessions, jjul_sessions, meso_sales, statistics

# --- 데이터베이스 테이블 생성 ---
try:
    print("데이터베이스 테이블 생성 시도...")
    models.Base.metadata.create_all(bind=database.engine)
    print("데이터베이스 테이블 확인/생성 완료.")
except Exception as e:
    print(f"데이터베이스 테이블 생성 중 오류 발생: {e}")
# --- 데이터베이스 테이블 생성 끝 ---

app = FastAPI(title="메이플스토리 수익 기록 웹 프로그램", version="1.0.0")

# --- 정적 파일 마운트 ---
app.mount("/static", StaticFiles(directory="static"), name="static")
# --- 정적 파일 마운트 끝 ---

# --- Jinja2 템플릿 설정 ---
templates = Jinja2Templates(directory="templates")
# --- Jinja2 템플릿 설정 끝 ---

# --- API 라우터 등록 ---
# 라우터 객체는 원래 _sessions 사용, prefix만 _times로 매핑

# hunting_sessions.router를 '/api/hunting-times' 경로에 연결
app.include_router(hunting_sessions.router, prefix="/api/hunting-times", tags=["hunting-times"]) # prefix를 '/api/hunting-times'로 설정

# jjul_sessions.router를 '/api/jjul-times' 경로에 연결
app.include_router(jjul_sessions.router, prefix="/api/jjul-times", tags=["jjul-times"]) # prefix를 '/api/jjul-times'로 설정

app.include_router(meso_sales.router, prefix="/api/meso-sales", tags=["meso-sales"])     # 변경 없음
app.include_router(statistics.router, prefix="/api/statistics", tags=["statistics"])     # 변경 없음
# --- API 라우터 등록 끝 ---

# --- UI 라우트 정의 ---
@app.get("/", response_class=HTMLResponse, name="read_home")
async def read_home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/meso-sales", response_class=HTMLResponse, name="meso_sales_page")
async def meso_sales_page(request: Request):
    return templates.TemplateResponse("list_and_add_meso_sales.html", {"request": request})

@app.get("/hunting-times", response_class=HTMLResponse, name="hunting_times_page")
async def hunting_times_page(request: Request):
    return templates.TemplateResponse("list_and_add_hunting_sessions.html", {"request": request})

@app.get("/jjul-times", response_class=HTMLResponse, name="jjul_times_page")
async def jjul_times_page(request: Request):
    return templates.TemplateResponse("list_and_add_jjul_sessions.html", {"request": request})

@app.get("/statistics/daily", response_class=HTMLResponse, name="statistics_daily_page")
async def statistics_daily_page(request: Request):
    return templates.TemplateResponse("statistics_daily.html", {"request": request})

@app.get("/statistics/map", response_class=HTMLResponse, name="statistics_map_page")
async def statistics_map_page(request: Request):
    return templates.TemplateResponse("statistics_map.html", {"request": request})

@app.get("/statistics/weekday", response_class=HTMLResponse, name="statistics_weekday_page")
async def statistics_weekday_page(request: Request):
    return templates.TemplateResponse("statistics_weekday.html", {"request": request})
# --- UI 라우트 정의 끝 ---

# --- 데이터베이스 의존성 ---
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()
# --- 데이터베이스 의존성 끝 ---

# --- 서버 실행 (개발용) ---
# if __name__ == "__main__":
#     uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
# --- 서버 실행 끝 ---