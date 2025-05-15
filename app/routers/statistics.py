# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, HTTPException, Query, Request 
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
import datetime

from .. import crud, schemas, database

# ================== ✨ 라우터 객체 생성 (필수) ✨ ==================
router = APIRouter()
# =================================================================

# --- 기존 수익 관련 통계 엔드포인트들 ---
@router.get("/summary/daily", response_model=schemas.DailySummaryResponse, tags=["Statistics - Profit"])
async def read_daily_summary(
    start_date: datetime.date = Query(..., description="조회 시작 날짜 (YYYY-MM-DD)"),
    end_date: datetime.date = Query(..., description="조회 종료 날짜 (YYYY-MM-DD)"),
    db: Session = Depends(database.get_db)
):
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="시작 날짜는 종료 날짜보다 이전이어야 합니다.")
    try:
        daily_summary_data = crud.get_daily_summary(db=db, start_date=start_date, end_date=end_date)
        return schemas.DailySummaryResponse(start_date=start_date, end_date=end_date, summaries=daily_summary_data)
    except Exception as e:
        print(f"Error in read_daily_summary: {e}")
        raise HTTPException(status_code=500, detail="일별 수익 요약 조회 중 내부 서버 오류가 발생했습니다.")


@router.get("/summary/map", response_model=schemas.MapSummaryResponse, tags=["Statistics - Profit"])
async def read_map_summary(
    start_date: Optional[datetime.date] = Query(None, description="조회 시작 날짜 (YYYY-MM-DD)"),
    end_date: Optional[datetime.date] = Query(None, description="조회 종료 날짜 (YYYY-MM-DD)"),
    db: Session = Depends(database.get_db)
):
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=400, detail="시작 날짜는 종료 날짜보다 이전이어야 합니다.")
    try:
        summary_data = crud.get_map_summary(db=db, start_date=start_date, end_date=end_date)
        return schemas.MapSummaryResponse(start_date=start_date, end_date=end_date, summaries=summary_data)
    except Exception as e:
        print(f"Error in read_map_summary: {e}")
        raise HTTPException(status_code=500, detail="맵별 수익 요약 조회 중 내부 서버 오류가 발생했습니다.")

@router.get("/summary/weekday", response_model=schemas.WeekdaySummaryResponse, tags=["Statistics - Profit"])
async def read_weekday_summary(
    start_date: Optional[datetime.date] = Query(None, description="조회 시작 날짜 (YYYY-MM-DD)"),
    end_date: Optional[datetime.date] = Query(None, description="조회 종료 날짜 (YYYY-MM-DD)"),
    db: Session = Depends(database.get_db)
):
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=400, detail="시작 날짜는 종료 날짜보다 이전이어야 합니다.")
    try:
        summary_data = crud.get_weekday_summary(db=db, start_date=start_date, end_date=end_date)
        return schemas.WeekdaySummaryResponse(start_date=start_date, end_date=end_date, summaries=summary_data)
    except Exception as e:
        print(f"Error in read_weekday_summary: {e}")
        raise HTTPException(status_code=500, detail="요일별 수익 요약 조회 중 내부 서버 오류가 발생했습니다.")

# --- 기존 경험치 통계 엔드포인트 (DailyExperienceSummaryItem 기반) ---
@router.get("/experience/summary/daily", response_model=schemas.DailyExperienceSummaryResponse, tags=["Statistics - Experience"])
async def read_daily_experience_summary(
    start_date: datetime.date = Query(..., description="조회 시작 날짜 (YYYY-MM-DD)"),
    end_date: datetime.date = Query(..., description="조회 종료 날짜 (YYYY-MM-DD)"),
    db: Session = Depends(database.get_db)
):
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="시작 날짜는 종료 날짜보다 이전이어야 합니다.")
    try:
        summary_data = crud.get_daily_experience_summary(db=db, start_date=start_date, end_date=end_date)
        return schemas.DailyExperienceSummaryResponse(start_date=start_date, end_date=end_date, summaries=summary_data)
    except Exception as e:
        print(f"Error in read_daily_experience_summary: {e}")
        raise HTTPException(status_code=500, detail="일별 경험치 요약 조회 중 내부 서버 오류가 발생했습니다.")


# ================== ✨ gained_exp 기반 경험치 통계 API 엔드포인트 (v2) ✨ ==================
@router.get("/experience/v2/average-per-hour", response_model=schemas.ExpAverageStats, tags=["Statistics - Experience (v2)"])
def read_average_exp_per_hour_v2(db: Session = Depends(database.get_db)):
    try:
        avg_exp = crud.get_average_exp_per_hour_v2(db=db)
        return schemas.ExpAverageStats(average_exp_per_hour=avg_exp)
    except Exception as e:
        print(f"Error calculating average exp per hour (v2): {e}")
        raise HTTPException(status_code=500, detail="시간당 평균 경험치(v2) 계산 중 내부 서버 오류가 발생했습니다.")

@router.get("/experience/v2/daily-details", response_model=schemas.ExpDailyStats, tags=["Statistics - Experience (v2)"])
def read_daily_exp_details_v2(
    start_date: Optional[datetime.date] = Query(None, description="시작 날짜 (YYYY-MM-DD)"),
    end_date: Optional[datetime.date] = Query(None, description="종료 날짜 (YYYY-MM-DD)"),
    db: Session = Depends(database.get_db)
):
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=400, detail="시작 날짜는 종료 날짜보다 이전이어야 합니다.")
    try:
        daily_exp_data = crud.get_daily_exp_values(db=db, start_date=start_date, end_date=end_date)
        return schemas.ExpDailyStats(daily_exp=daily_exp_data)
    except Exception as e:
        print(f"Error calculating daily exp details (v2): {e}")
        raise HTTPException(status_code=500, detail="일별 상세 경험치(v2) 계산 중 내부 서버 오류가 발생했습니다.")

# ====================================================================================

# ================== ✨ 요일별 경험치 통계 API 엔드포인트 ✨ ==================
@router.get(
    "/experience/summary/weekday",
    response_model=schemas.ExperienceWeekdaySummaryResponse,
    tags=["Statistics - Experience"] 
)
async def read_experience_summary_by_weekday(
    # request: Request, # 현재 사용되지 않으므로 제거
    start_date: Optional[datetime.date] = Query(None, description="조회 시작 날짜 (YYYY-MM-DD)"),
    end_date: Optional[datetime.date] = Query(None, description="조회 종료 날짜 (YYYY-MM-DD)"),
    db: Session = Depends(database.get_db)
):
    """
    지정된 기간 또는 전체 기간에 대한 요일별 경험치 요약 통계를 반환합니다.
    - **start_date**: 조회 시작 날짜 (YYYY-MM-DD 형식)
    - **end_date**: 조회 종료 날짜 (YYYY-MM-DD 형식)
    두 날짜 모두 제공되지 않으면 전체 기간을 대상으로 합니다.
    """
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=400, detail="시작 날짜는 종료 날짜보다 이전이어야 합니다.")

    try:
        summary_data = crud.get_experience_summary_by_weekday(db=db, start_date=start_date, end_date=end_date)
        
        return schemas.ExperienceWeekdaySummaryResponse(
            start_date=start_date,
            end_date=end_date,
            summaries=summary_data
        )
    except Exception as e:
        print(f"Error in read_experience_summary_by_weekday: {e}")
        raise HTTPException(status_code=500, detail="요일별 경험치 통계 조회 중 내부 서버 오류가 발생했습니다.")
# =======================================================================================

# ================== ✨ 맵별 경험치 통계 API 엔드포인트 (신규 추가) ✨ ==================
@router.get(
    "/experience/summary/map", 
    response_model=schemas.ExperienceMapSummaryResponse,
    tags=["Statistics - Experience"] 
)
async def read_experience_summary_by_map(
    # request: Request, # 현재 사용되지 않으므로 제거
    start_date: Optional[datetime.date] = Query(None, description="조회 시작 날짜 (YYYY-MM-DD)"),
    end_date: Optional[datetime.date] = Query(None, description="조회 종료 날짜 (YYYY-MM-DD)"),
    db: Session = Depends(database.get_db)
):
    """
    지정된 기간 또는 전체 기간에 대한 맵별 경험치 요약 통계를 반환합니다.
    - **start_date**: 조회 시작 날짜 (YYYY-MM-DD 형식)
    - **end_date**: 조회 종료 날짜 (YYYY-MM-DD 형식)
    두 날짜 모두 제공되지 않으면 전체 기간을 대상으로 합니다.
    """
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=400, detail="시작 날짜는 종료 날짜보다 이전이어야 합니다.")

    try:
        summary_data = crud.get_experience_summary_by_map(db=db, start_date=start_date, end_date=end_date)
        
        return schemas.ExperienceMapSummaryResponse(
            start_date=start_date,
            end_date=end_date,
            summaries=summary_data
        )
    except Exception as e:
        print(f"Error in read_experience_summary_by_map: {e}")
        raise HTTPException(status_code=500, detail="맵별 경험치 통계 조회 중 내부 서버 오류가 발생했습니다.")
# =====================================================================================


# --- 자동 완성을 위한 고유 이름 목록 API ---
@router.get("/unique-names/maps", response_model=List[str], tags=["Utility - Unique Names"])
def get_unique_map_names_api(db: Session = Depends(database.get_db)):
    try:
        return crud.get_unique_map_names(db)
    except Exception as e:
        print(f"Error in get_unique_map_names_api: {e}")
        raise HTTPException(status_code=500, detail="맵 이름 목록 조회 중 오류가 발생했습니다.")

@router.get("/unique-names/rare-items", response_model=List[str], tags=["Utility - Unique Names"])
def get_unique_rare_item_names_api(db: Session = Depends(database.get_db)):
    try:
        return crud.get_unique_rare_item_names(db)
    except Exception as e:
        print(f"Error in get_unique_rare_item_names_api: {e}")
        raise HTTPException(status_code=500, detail="고가 아이템 이름 목록 조회 중 오류가 발생했습니다.")

@router.get("/unique-names/consumable-items", response_model=List[str], tags=["Utility - Unique Names"])
def get_unique_consumable_item_names_api(db: Session = Depends(database.get_db)):
    try:
        return crud.get_unique_consumable_item_names(db)
    except Exception as e:
        print(f"Error in get_unique_consumable_item_names_api: {e}")
        raise HTTPException(status_code=500, detail="소모 아이템 이름 목록 조회 중 오류가 발생했습니다.")
# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, HTTPException, Query, Request 
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
import datetime

from .. import crud, schemas, database

# ================== ✨ 라우터 객체 생성 (필수) ✨ ==================
router = APIRouter()
# =================================================================

# --- 기존 수익 관련 통계 엔드포인트들 ---
@router.get("/summary/daily", response_model=schemas.DailySummaryResponse, tags=["Statistics - Profit"])
async def read_daily_summary(
    start_date: datetime.date = Query(..., description="조회 시작 날짜 (YYYY-MM-DD)"),
    end_date: datetime.date = Query(..., description="조회 종료 날짜 (YYYY-MM-DD)"),
    db: Session = Depends(database.get_db)
):
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="시작 날짜는 종료 날짜보다 이전이어야 합니다.")
    try:
        daily_summary_data = crud.get_daily_summary(db=db, start_date=start_date, end_date=end_date)
        return schemas.DailySummaryResponse(start_date=start_date, end_date=end_date, summaries=daily_summary_data)
    except Exception as e:
        print(f"Error in read_daily_summary: {e}")
        raise HTTPException(status_code=500, detail="일별 수익 요약 조회 중 내부 서버 오류가 발생했습니다.")


@router.get("/summary/map", response_model=schemas.MapSummaryResponse, tags=["Statistics - Profit"])
async def read_map_summary(
    start_date: Optional[datetime.date] = Query(None, description="조회 시작 날짜 (YYYY-MM-DD)"),
    end_date: Optional[datetime.date] = Query(None, description="조회 종료 날짜 (YYYY-MM-DD)"),
    db: Session = Depends(database.get_db)
):
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=400, detail="시작 날짜는 종료 날짜보다 이전이어야 합니다.")
    try:
        summary_data = crud.get_map_summary(db=db, start_date=start_date, end_date=end_date)
        return schemas.MapSummaryResponse(start_date=start_date, end_date=end_date, summaries=summary_data)
    except Exception as e:
        print(f"Error in read_map_summary: {e}")
        raise HTTPException(status_code=500, detail="맵별 수익 요약 조회 중 내부 서버 오류가 발생했습니다.")

@router.get("/summary/weekday", response_model=schemas.WeekdaySummaryResponse, tags=["Statistics - Profit"])
async def read_weekday_summary(
    start_date: Optional[datetime.date] = Query(None, description="조회 시작 날짜 (YYYY-MM-DD)"),
    end_date: Optional[datetime.date] = Query(None, description="조회 종료 날짜 (YYYY-MM-DD)"),
    db: Session = Depends(database.get_db)
):
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=400, detail="시작 날짜는 종료 날짜보다 이전이어야 합니다.")
    try:
        summary_data = crud.get_weekday_summary(db=db, start_date=start_date, end_date=end_date)
        return schemas.WeekdaySummaryResponse(start_date=start_date, end_date=end_date, summaries=summary_data)
    except Exception as e:
        print(f"Error in read_weekday_summary: {e}")
        raise HTTPException(status_code=500, detail="요일별 수익 요약 조회 중 내부 서버 오류가 발생했습니다.")

# --- 기존 경험치 통계 엔드포인트 (DailyExperienceSummaryItem 기반) ---
@router.get("/experience/summary/daily", response_model=schemas.DailyExperienceSummaryResponse, tags=["Statistics - Experience"])
async def read_daily_experience_summary(
    start_date: datetime.date = Query(..., description="조회 시작 날짜 (YYYY-MM-DD)"),
    end_date: datetime.date = Query(..., description="조회 종료 날짜 (YYYY-MM-DD)"),
    db: Session = Depends(database.get_db)
):
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="시작 날짜는 종료 날짜보다 이전이어야 합니다.")
    try:
        summary_data = crud.get_daily_experience_summary(db=db, start_date=start_date, end_date=end_date)
        return schemas.DailyExperienceSummaryResponse(start_date=start_date, end_date=end_date, summaries=summary_data)
    except Exception as e:
        print(f"Error in read_daily_experience_summary: {e}")
        raise HTTPException(status_code=500, detail="일별 경험치 요약 조회 중 내부 서버 오류가 발생했습니다.")


# ================== ✨ gained_exp 기반 경험치 통계 API 엔드포인트 (v2) ✨ ==================
@router.get("/experience/v2/average-per-hour", response_model=schemas.ExpAverageStats, tags=["Statistics - Experience (v2)"])
def read_average_exp_per_hour_v2(db: Session = Depends(database.get_db)):
    try:
        avg_exp = crud.get_average_exp_per_hour_v2(db=db)
        return schemas.ExpAverageStats(average_exp_per_hour=avg_exp)
    except Exception as e:
        print(f"Error calculating average exp per hour (v2): {e}")
        raise HTTPException(status_code=500, detail="시간당 평균 경험치(v2) 계산 중 내부 서버 오류가 발생했습니다.")

@router.get("/experience/v2/daily-details", response_model=schemas.ExpDailyStats, tags=["Statistics - Experience (v2)"])
def read_daily_exp_details_v2(
    start_date: Optional[datetime.date] = Query(None, description="시작 날짜 (YYYY-MM-DD)"),
    end_date: Optional[datetime.date] = Query(None, description="종료 날짜 (YYYY-MM-DD)"),
    db: Session = Depends(database.get_db)
):
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=400, detail="시작 날짜는 종료 날짜보다 이전이어야 합니다.")
    try:
        daily_exp_data = crud.get_daily_exp_values(db=db, start_date=start_date, end_date=end_date)
        return schemas.ExpDailyStats(daily_exp=daily_exp_data)
    except Exception as e:
        print(f"Error calculating daily exp details (v2): {e}")
        raise HTTPException(status_code=500, detail="일별 상세 경험치(v2) 계산 중 내부 서버 오류가 발생했습니다.")

# ====================================================================================

# ================== ✨ 요일별 경험치 통계 API 엔드포인트 ✨ ==================
@router.get(
    "/experience/summary/weekday",
    response_model=schemas.ExperienceWeekdaySummaryResponse,
    tags=["Statistics - Experience"] 
)
async def read_experience_summary_by_weekday(
    # request: Request, # 현재 사용되지 않으므로 제거
    start_date: Optional[datetime.date] = Query(None, description="조회 시작 날짜 (YYYY-MM-DD)"),
    end_date: Optional[datetime.date] = Query(None, description="조회 종료 날짜 (YYYY-MM-DD)"),
    db: Session = Depends(database.get_db)
):
    """
    지정된 기간 또는 전체 기간에 대한 요일별 경험치 요약 통계를 반환합니다.
    - **start_date**: 조회 시작 날짜 (YYYY-MM-DD 형식)
    - **end_date**: 조회 종료 날짜 (YYYY-MM-DD 형식)
    두 날짜 모두 제공되지 않으면 전체 기간을 대상으로 합니다.
    """
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=400, detail="시작 날짜는 종료 날짜보다 이전이어야 합니다.")

    try:
        summary_data = crud.get_experience_summary_by_weekday(db=db, start_date=start_date, end_date=end_date)
        
        return schemas.ExperienceWeekdaySummaryResponse(
            start_date=start_date,
            end_date=end_date,
            summaries=summary_data
        )
    except Exception as e:
        print(f"Error in read_experience_summary_by_weekday: {e}")
        raise HTTPException(status_code=500, detail="요일별 경험치 통계 조회 중 내부 서버 오류가 발생했습니다.")
# =======================================================================================

# ================== ✨ 맵별 경험치 통계 API 엔드포인트 (신규 추가) ✨ ==================
@router.get(
    "/experience/summary/map", 
    response_model=schemas.ExperienceMapSummaryResponse,
    tags=["Statistics - Experience"] 
)
async def read_experience_summary_by_map(
    # request: Request, # 현재 사용되지 않으므로 제거
    start_date: Optional[datetime.date] = Query(None, description="조회 시작 날짜 (YYYY-MM-DD)"),
    end_date: Optional[datetime.date] = Query(None, description="조회 종료 날짜 (YYYY-MM-DD)"),
    db: Session = Depends(database.get_db)
):
    """
    지정된 기간 또는 전체 기간에 대한 맵별 경험치 요약 통계를 반환합니다.
    - **start_date**: 조회 시작 날짜 (YYYY-MM-DD 형식)
    - **end_date**: 조회 종료 날짜 (YYYY-MM-DD 형식)
    두 날짜 모두 제공되지 않으면 전체 기간을 대상으로 합니다.
    """
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=400, detail="시작 날짜는 종료 날짜보다 이전이어야 합니다.")

    try:
        summary_data = crud.get_experience_summary_by_map(db=db, start_date=start_date, end_date=end_date)
        
        return schemas.ExperienceMapSummaryResponse(
            start_date=start_date,
            end_date=end_date,
            summaries=summary_data
        )
    except Exception as e:
        print(f"Error in read_experience_summary_by_map: {e}")
        raise HTTPException(status_code=500, detail="맵별 경험치 통계 조회 중 내부 서버 오류가 발생했습니다.")
# =====================================================================================


# --- 자동 완성을 위한 고유 이름 목록 API ---
@router.get("/unique-names/maps", response_model=List[str], tags=["Utility - Unique Names"])
def get_unique_map_names_api(db: Session = Depends(database.get_db)):
    try:
        return crud.get_unique_map_names(db)
    except Exception as e:
        print(f"Error in get_unique_map_names_api: {e}")
        raise HTTPException(status_code=500, detail="맵 이름 목록 조회 중 오류가 발생했습니다.")

@router.get("/unique-names/rare-items", response_model=List[str], tags=["Utility - Unique Names"])
def get_unique_rare_item_names_api(db: Session = Depends(database.get_db)):
    try:
        return crud.get_unique_rare_item_names(db)
    except Exception as e:
        print(f"Error in get_unique_rare_item_names_api: {e}")
        raise HTTPException(status_code=500, detail="고가 아이템 이름 목록 조회 중 오류가 발생했습니다.")

@router.get("/unique-names/consumable-items", response_model=List[str], tags=["Utility - Unique Names"])
def get_unique_consumable_item_names_api(db: Session = Depends(database.get_db)):
    try:
        return crud.get_unique_consumable_item_names(db)
    except Exception as e:
        print(f"Error in get_unique_consumable_item_names_api: {e}")
        raise HTTPException(status_code=500, detail="소모 아이템 이름 목록 조회 중 오류가 발생했습니다.")
@router.get("/experience/v2/test-route")
async def test_experience_route():
    return {"message": "Experience test route is working!"}