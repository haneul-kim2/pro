# C:\pro\main.py (수정안 - V5 백업 기준 이름으로 복구 시도)

# ================== 필요한 라이브러리 임포트 ==================
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import os
import datetime # 파일 상단에 추가

from app import crud, models, schemas, database
from app.routers import hunting_sessions, jjul_sessions, meso_sales, statistics
from app.database import get_db # get_db는 database 모듈 안에 정의된 것을 사용

# FastAPI 앱 인스턴스 생성
app = FastAPI(
    title="메이플스토리 수익 기록 웹 프로그램",
    description="메이플스토리 활동으로 얻는 수익을 기록하고 통계를 제공하는 웹 애플리케이션",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    try:
        print("데이터베이스 테이블 생성 시도 (startup 이벤트)...")
        models.Base.metadata.create_all(bind=database.engine) # database.engine 사용
        print("데이터베이스 테이블 확인/생성 완료 (startup 이벤트).")
    except Exception as e:
        print(f"데이터베이스 테이블 생성 중 오류 발생 (startup 이벤트): {e}")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# get_db 함수는 app.database 모듈에서 가져오므로 여기서 재정의할 필요 없음

# ================== API 라우터 등록 ==================
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
@app.get("/", response_class=HTMLResponse, name="home", tags=["UI Pages"]) # V5 기준: "home"
async def read_home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/hunting-times/", response_class=HTMLResponse, name="list_and_add_hunting_sessions", tags=["UI Pages"])
async def list_and_add_hunting_sessions_page(request: Request, db: Session = Depends(get_db)): # db: Session 추가
    hunting_sessions_data = crud.get_hunting_sessions(db=db, skip=0, limit=100) # DB에서 데이터 조회
    return templates.TemplateResponse(
        "list_and_add_hunting_sessions.html", 
        {"request": request, "hunting_sessions": hunting_sessions_data} # 조회한 데이터를 템플릿에 전달
    )

@app.get("/jjul-times/", response_class=HTMLResponse, name="list_and_add_jjul_sessions", tags=["UI Pages"]) # V5 기준 및 경로에 / 추가
async def list_and_add_jjul_sessions_page(request: Request, db: Session = Depends(get_db)): # 함수 이름 변경 및 db 의존성 추가
    jjul_sessions_data = crud.get_jjul_sessions(db=db, skip=0, limit=100) # 예시 데이터 로드
    return templates.TemplateResponse("list_and_add_jjul_sessions.html", {"request": request, "jjul_sessions": jjul_sessions_data})

@app.get("/meso-sales/", response_class=HTMLResponse, name="list_and_add_meso_sales", tags=["UI Pages"]) # 이것은 이미 V5 기준과 일치
async def list_and_add_meso_sales_page(request: Request, db: Session = Depends(get_db)): # 함수 이름 일관성 위해 _page 추가 (선택)
    meso_sales_data = crud.get_meso_sales(db=db, skip=0, limit=100)
    return templates.TemplateResponse(
        "list_and_add_meso_sales.html",
        {"request": request, "meso_sales": meso_sales_data}
    )

@app.get("/statistics/daily/", response_class=HTMLResponse, name="statistics_daily", tags=["UI Pages"]) # V5 기준 및 경로에 / 추가
async def statistics_daily_page_ui(request: Request): # 함수 이름 변경
    return templates.TemplateResponse("statistics_daily.html", {"request": request})

@app.get("/statistics/map/", response_class=HTMLResponse, name="statistics_map", tags=["UI Pages"]) # V5 기준 및 경로에 / 추가
async def statistics_map_page_ui(request: Request): # 함수 이름 변경
    return templates.TemplateResponse("statistics_map.html", {"request": request})

@app.get("/statistics/weekday/", response_class=HTMLResponse, name="statistics_weekday", tags=["UI Pages"]) # V5 기준 및 경로에 / 추가
async def statistics_weekday_page_ui(request: Request): # 함수 이름 변경
    return templates.TemplateResponse("statistics_weekday.html", {"request": request})

# 경험치 통계 페이지는 V5 백업에 없었으므로, 현재 이름 유지 또는 다른 UI 페이지와 규칙 통일
@app.get("/statistics/experience/", response_class=HTMLResponse, name="statistics_experience", tags=["UI Pages"]) # 이름 간결화 및 경로에 / 추가
async def statistics_experience_page_ui(request: Request): # 함수 이름 변경
    return templates.TemplateResponse("statistics_experience.html", {"request": request})
# main.py 에 추가
@app.get("/statistics/experience/weekday/", response_class=HTMLResponse, name="statistics_experience_weekday", tags=["UI Pages - Experience Statistics"])
async def statistics_experience_weekday_page_ui(request: Request):
    return templates.TemplateResponse("statistics_experience_weekday.html", {"request": request})
# --- 경험치 통계 관련 라우트 ---
@app.get("/statistics/experience/", response_class=HTMLResponse, name="statistics_experience_daily", tags=["UI Pages - Experience Statistics"]) # name 변경
async def statistics_experience_daily_page_ui(request: Request): # 함수 이름도 일관성 있게 변경 가능 (선택 사항)
    return templates.TemplateResponse("statistics_experience.html", {"request": request}) # 이 페이지가 '일별 경험치 요약' 역할

@app.get("/statistics/experience/weekday/", response_class=HTMLResponse, name="statistics_experience_weekday", tags=["UI Pages - Experience Statistics"])
async def statistics_experience_weekday_page_ui(request: Request):
    return templates.TemplateResponse("statistics_experience_weekday.html", {"request": request})

# main.py 에 있는 기존 임시 라우트를 아래와 같이 수정
@app.get("/statistics/experience/map/", response_class=HTMLResponse, name="statistics_experience_map", tags=["UI Pages - Experience Statistics"])
async def statistics_experience_map_page_ui(request: Request):
    return templates.TemplateResponse("statistics_experience_map.html", {"request": request}) # 실제 파일명으로 변경
# ================== UI 페이지 라우트 정의 끝 ==================
@app.get("/info", response_class=HTMLResponse, name="info_page", tags=["UI Pages"])
async def information_page(request: Request):
    creator_info = {
        "name": "김하늘",
        "discord_id": "gomsky",
        "youtube_name": "https://www.youtube.com/@rhahanul", # 이 부분을 클릭해서 이스터에그 발동
        "account_number": "카카오뱅크 3333-03-1751818",
        "nickname": "의문의돌맹이"  # ✨ 메랜 닉네임 추가 ✨
    }
    current_year = datetime.datetime.now().year
    return templates.TemplateResponse("info.html", {
        "request": request,
        "creator": creator_info,
        "current_year": current_year
    })
