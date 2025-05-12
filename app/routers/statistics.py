# C:\pro\app\routers\statistics.py (재확인 및 수정)

# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
import datetime

from .. import crud, schemas, database # ✨ database 모듈 import 확인 ✨

# ================== ✨ 라우터 객체 생성 (필수) ✨ ==================
router = APIRouter()
# =================================================================

# --- 기존 수익 관련 통계 엔드포인트들 ---
@router.get("/summary/daily", response_model=schemas.DailySummaryResponse, tags=["Statistics - Profit"])
async def read_daily_summary(
    start_date: datetime.date = Query(..., description="조회 시작 날짜 (YYYY-MM-DD)"),
    end_date: datetime.date = Query(..., description="조회 종료 날짜 (YYYY-MM-DD)"),
    db: Session = Depends(database.get_db) # ✨ database.get_db 사용 ✨
):
    # ... (함수 내용) ...
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="시작 날짜는 종료 날짜보다 이전이어야 합니다.")
    daily_summary_data = crud.get_daily_summary(db=db, start_date=start_date, end_date=end_date)
    return schemas.DailySummaryResponse(start_date=start_date, end_date=end_date, summaries=daily_summary_data)

# ... (read_map_summary, read_weekday_summary, read_daily_experience_summary - 모두 Depends(database.get_db) 사용 확인) ...
# ... (get_unique_map_names 등 자동 완성 API - 모두 Depends(database.get_db) 사용 확인) ...

# ================== ✨ gained_exp 기반 경험치 통계 API 엔드포인트 (신규) ✨ ==================
@router.get("/experience/v2/average-per-hour", response_model=schemas.ExpAverageStats, tags=["Statistics - Experience (v2)"])
def read_average_exp_per_hour_v2(db: Session = Depends(database.get_db)): # ✨ database.get_db 사용 ✨
    # ... (함수 내용) ...
    try:
        avg_exp = crud.get_average_exp_per_hour_v2(db=db)
        return {"average_exp_per_hour": avg_exp}
    except Exception as e:
        print(f"Error calculating average exp per hour (v2): {e}")
        raise HTTPException(status_code=500, detail="Internal server error while calculating average exp per hour (v2).")

@router.get("/experience/v2/daily-total", response_model=schemas.ExpDailyStats, tags=["Statistics - Experience (v2)"])
def read_daily_total_exp_v2(
    start_date_str: Optional[str] = Query(None, description="시작 날짜 (YYYY-MM-DD)", regex=r"^\d{4}-\d{2}-\d{2}$"),
    end_date_str: Optional[str] = Query(None, description="종료 날짜 (YYYY-MM-DD)", regex=r"^\d{4}-\d{2}-\d{2}$"),
    db: Session = Depends(database.get_db) # ✨ database.get_db 사용 ✨
):
    # ... (함수 내용) ...
    parsed_start_date = None
    parsed_end_date = None
    if start_date_str:
        try:
            parsed_start_date = datetime.date.fromisoformat(start_date_str)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD.")
    if end_date_str:
        try:
            parsed_end_date = datetime.date.fromisoformat(end_date_str)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD.")
    if parsed_start_date and parsed_end_date and parsed_start_date > parsed_end_date:
         raise HTTPException(status_code=400, detail="Start date cannot be after end date.")
    try:
        daily_exp_data = crud.get_daily_total_exp_v2(db=db, start_date=parsed_start_date, end_date=parsed_end_date)
        return {"daily_exp": daily_exp_data}
    except Exception as e:
        print(f"Error calculating daily total exp (v2): {e}")
        raise HTTPException(status_code=500, detail="Internal server error while calculating daily total exp (v2).")
# ====================================================================================