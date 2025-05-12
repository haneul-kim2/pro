# C:\pro\main.py (정리 및 확인 중점)

import uvicorn  # uvicorn import 추가 (만약 아래 if __name__ == "__main__": 사용 고려 시)
from fastapi import FastAPI, Request, Depends, HTTPException  # 필요한 모듈 import 확인
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app import models, schemas, crud, database
# 라우터 import 확인 - 모든 필요한 라우터가 있는지 확인
from app.routers import hunting_sessions, jjul_sessions, meso_sales, statistics

# --- 데이터베이스 테이블 생성 ---
# 앱 시작 시 DB 테이블 확인 및 생성 (DB 재생성 방식에 적합)
try:
    print("데이터베이스 테이블 생성 시도...")
    models.Base.metadata.create_all(bind=database.engine)
    print("데이터베이스 테이블 확인/생성 완료.")
except Exception as e:
    print(f"데이터베이스 테이블 생성 중 오류 발생: {e}")
# --- 데이터베이스 테이블 생성 끝 ---

# FastAPI 앱 인스턴스 생성
app = FastAPI(
    title="메이플스토리 수익 기록 웹 프로그램",
    description="메이플스토리 활동으로 얻는 수익을 기록하고 통계를 제공하는 웹 애플리케이션",
    version="1.0.0"
)

# --- 정적 파일 마운트 ---
# '/static' URL 경로로 요청이 오면 'static' 디렉토리의 파일을 제공
app.mount("/static", StaticFiles(directory="static"), name="static")
# --- 정적 파일 마운트 끝 ---

# --- Jinja2 템플릿 설정 ---
# HTML 템플릿 파일이 있는 디렉토리 지정
templates = Jinja2Templates(directory="templates")
# --- Jinja2 템플릿 설정 끝 ---

# --- 데이터베이스 의존성 함수 ---
# 각 요청 처리 시 DB 세션을 얻기 위한 함수
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()
# --- 데이터베이스 의존성 함수 끝 ---


# ================== API 라우터 등록 ==================
# 각 라우터 모듈의 경로들을 특정 prefix 뒤에 연결합니다.

# '/api/hunting-times' 로 시작하는 경로는 hunting_sessions 라우터가 처리
app.include_router(
    hunting_sessions.router,
    prefix="/api/hunting-times",
    tags=["Hunting Times API"] # 태그 이름 명확화 (선택적)
)

# '/api/jjul-times' 로 시작하는 경로는 jjul_sessions 라우터가 처리
app.include_router(
    jjul_sessions.router,
    prefix="/api/jjul-times",
    tags=["Jjul Times API"] # 태그 이름 명확화 (선택적)
)

# '/api/meso-sales' 로 시작하는 경로는 meso_sales 라우터가 처리
app.include_router(
    meso_sales.router,
    prefix="/api/meso-sales",
    tags=["Meso Sales API"] # 태그 이름 명확화 (선택적)
)

# '/api/statistics' 로 시작하는 경로는 statistics 라우터가 처리
app.include_router(
    statistics.router,
    prefix="/api/statistics",
    tags=["Statistics API"] # 태그 이름 명확화 (선택적)
)
# ================== API 라우터 등록 끝 ==================


# ================== UI 페이지 라우트 정의 ==================
# 웹 브라우저에서 접속하는 각 페이지 경로 처리

@app.get("/", response_class=HTMLResponse, name="read_home", tags=["UI Pages"])
async def read_home(request: Request):
    """메인 홈 페이지를 반환합니다."""
    return templates.TemplateResponse("home.html", {"request": request})

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
    # 로그에 나왔던 /ui/ 경로는 없으므로, 이 경로가 맞는지 확인
    return templates.TemplateResponse("statistics_weekday.html", {"request": request})

# --- ✨ 경험치 통계 페이지 라우트 (아직 없음 - 필요시 추가) ---
# @app.get("/statistics/experience", response_class=HTMLResponse, name="statistics_experience_page", tags=["UI Pages"])
# async def statistics_experience_page(request: Request):
#     """경험치 통계 페이지를 반환합니다."""
#     # return templates.TemplateResponse("statistics_experience.html", {"request": request}) # 해당 HTML 파일 생성 필요
#     pass # 아직 페이지 없으므로 pass

# ================== UI 페이지 라우트 정의 끝 ==================


# --- 개발 서버 실행 (선택적) ---
# uvicorn 명령어로 직접 실행하는 경우 이 부분은 없어도 됩니다.
# if __name__ == "__main__":
#     print("개발 서버를 시작합니다...")
#     uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
# --- 개발 서버 실행 끝 ---