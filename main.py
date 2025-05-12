# C:\pro\main.py

# 1. FastAPI 및 관련 모듈 임포트
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import Response # favicon 용
import os
from sqlalchemy.orm import Session # DB 세션 타입 힌팅용
from fastapi.responses import HTMLResponse

# 2. 우리 앱의 모듈 임포트
from app.database import engine, Base, SessionLocal
import app.models # models.py의 테이블 정의를 인식시킵니다.

# API 라우터 임포트
from app.routers import meso_sales as meso_sales_api_router
from app.routers import hunting_sessions as hunting_sessions_api_router
from app.routers import jjul_sessions as jjul_sessions_api_router # <--- 쩔 세션 API 라우터 임포트
from app.routers import statistics as statistics_api_router
# CRUD 모듈 임포트
from app import crud

# 3. FastAPI 애플리케이션 인스턴스 생성
app = FastAPI(
    title="메이플스토리 수익 기록 웹앱",
    description="기존 Tkinter 프로그램을 웹으로 전환하는 프로젝트입니다.",
    version="0.1.0",
)

# 4. 정적 파일 (CSS, JS, 이미지 등) 제공 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# 5. Jinja2 템플릿 설정
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# 6. 데이터베이스 세션 의존성 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 7. 애플리케이션 시작 시 실행될 이벤트 핸들러
@app.on_event("startup")
async def startup_event():
    print("애플리케이션 시작! 데이터베이스 테이블 생성을 시도합니다...")
    try:
        Base.metadata.create_all(bind=engine)
        print("데이터베이스 테이블 생성 또는 확인 완료.")
    except Exception as e:
        print(f"데이터베이스 테이블 생성 중 오류 발생: {e}")

# 8. Favicon.ico 처리
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(content=b'', media_type="image/x-icon", status_code=200)

# 9. 웹 UI를 위한 라우트
@app.get("/", tags=["UI"], name="read_root_page_ui")
async def read_root_page_ui(request: Request):
    return templates.TemplateResponse("home.html", {
        "request": request,
        "page_title": "메이플 수익 기록 웹앱",
        "docs_url": app.docs_url,
        "redoc_url": app.redoc_url,
        "list_meso_sales_url": app.url_path_for("ui_list_and_add_meso_sales_page"),
        "list_hunting_sessions_url": app.url_path_for("ui_list_and_add_hunting_sessions_page"),
        "list_jjul_sessions_url": app.url_path_for("ui_list_and_add_jjul_sessions_page") # <--- 쩔 세션 UI 페이지 링크용 (아직 안 만듦)
    })

@app.get("/ui/meso-sales/list", tags=["UI"], name="ui_list_and_add_meso_sales_page")
async def ui_list_and_add_meso_sales_page(request: Request, db: Session = Depends(get_db)):
    logs = []
    try:
        logs = crud.get_meso_sale_logs(db=db, limit=100)
    except Exception as e:
        print(f"Error in ui_list_and_add_meso_sales_page getting logs: {e}")
    
    return templates.TemplateResponse("list_and_add_meso_sales.html", {
        "request": request,
        "page_title": "메소 판매 기록 관리",
        "meso_sales_logs": logs,
        "message": None, 
        "message_type": None
    })

@app.get("/ui/hunting-sessions/list", tags=["UI"], name="ui_list_and_add_hunting_sessions_page")
async def ui_list_and_add_hunting_sessions_page(request: Request):
    return templates.TemplateResponse("list_and_add_hunting_sessions.html", {
        "request": request,
        "page_title": "사냥 기록 관리",
        "message": None,
        "message_type": None
    })

# --- 쩔 세션 UI 페이지 라우트 (아직 HTML 파일은 없음) ---
@app.get("/ui/jjul-sessions/list", tags=["UI"], name="ui_list_and_add_jjul_sessions_page")
async def ui_list_and_add_jjul_sessions_page(request: Request):
    # 이 페이지는 아직 HTML 템플릿을 만들지 않았습니다.
    # 지금은 간단한 메시지만 반환하거나, 나중에 템플릿을 만들고 연결합니다.
    # return {"message": "쩔 세션 기록 페이지 - 준비 중"}
    return templates.TemplateResponse("list_and_add_jjul_sessions.html", { # 이 HTML 파일 필요
        "request": request,
        "page_title": "쩔 기록 관리",
        "message": None,
        "message_type": None
    })
# --- 여기까지 쩔 세션 UI 페이지 라우트 ---
# --- (쩔 세션 UI 페이지 라우트 아래 또는 비슷한 위치에) ---
@app.get("/ui/statistics/daily", tags=["UI"], name="ui_statistics_daily_page")
async def ui_statistics_daily_page(request: Request):
    return templates.TemplateResponse("statistics_daily.html", {
        "request": request,
        "page_title": "일별 요약 통계" 
        # message, message_type은 이 페이지에서는 초기값이 필요 없을 수 있습니다.
        # JavaScript가 API 호출 후 동적으로 메시지를 관리합니다.
    })
# ... (기존 코드, ui_statistics_daily_page 함수 아래 또는 비슷한 위치에) ...

@app.get("/ui/statistics/map", tags=["UI"], name="ui_statistics_map_page")
async def ui_statistics_map_page(request: Request):
    # 임시 테스트 코드 및 잘못된 주석 제거 후, 올바른 템플릿 응답으로 수정
    return templates.TemplateResponse("statistics_map.html", { # <-- 렌더링할 HTML 파일명 수정
        "request": request,
        "page_title": "맵별 요약 통계" # <-- 페이지 제목 수정
    })


# ... (app.include_router 부분) ...
@app.get("/ui/statistics/weekday", tags=["UI"], name="ui_statistics_weekday_page")
async def ui_statistics_weekday_page(request: Request):
    return templates.TemplateResponse("statistics_weekday.html", {
        "request": request,
        "page_title": "요일별 요약 통계"
    })


# 10. API 라우터 포함
app.include_router(meso_sales_api_router.router)
app.include_router(hunting_sessions_api_router.router)
app.include_router(jjul_sessions_api_router.router)
app.include_router(meso_sales_api_router.router)
app.include_router(hunting_sessions_api_router.router)
app.include_router(jjul_sessions_api_router.router)
app.include_router(statistics_api_router.router) # <--- 쩔 세션 API 라우터 등록


# --- 이 아래는 Uvicorn으로 실행할 때 직접 실행되지 않도록 하는 코드 (선택 사항) ---
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)