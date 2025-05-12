# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, HTTPException, Query # HTTPException, Query 추가 확인
from sqlalchemy.orm import Session
from typing import List, Optional
import datetime

# 현재 폴더(routers)의 상위 폴더(app)에 있는 crud, schemas, database 모듈을 가져옴
from .. import crud, schemas, database

# APIRouter 인스턴스 생성
router = APIRouter()

# =========================================
# Statistics API Endpoints
# =========================================

# --- 수익 관련 통계 ---

@router.get("/summary/daily", response_model=schemas.DailySummaryResponse, tags=["Statistics - Profit"])
async def read_daily_summary(
    start_date: datetime.date = Query(..., description="조회 시작 날짜 (YYYY-MM-DD)"),
    end_date: datetime.date = Query(..., description="조회 종료 날짜 (YYYY-MM-DD)"),
    db: Session = Depends(database.get_db)
):
    """
    지정된 기간 동안의 일별 수익 요약 통계를 조회합니다.
    """
    # 날짜 유효성 검사 추가
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="시작 날짜는 종료 날짜보다 이전이어야 합니다.")

    daily_summary_data = crud.get_daily_summary(db=db, start_date=start_date, end_date=end_date)
    return schemas.DailySummaryResponse(start_date=start_date, end_date=end_date, summaries=daily_summary_data)


@router.get("/summary/map", response_model=schemas.MapSummaryResponse, tags=["Statistics - Profit"])
async def read_map_summary(
    start_date: Optional[datetime.date] = Query(None, description="조회 시작 날짜 (YYYY-MM-DD, 선택 사항)"),
    end_date: Optional[datetime.date] = Query(None, description="조회 종료 날짜 (YYYY-MM-DD, 선택 사항)"),
    db: Session = Depends(database.get_db)
):
    """
    맵별 수익 통계를 조회합니다. 기간을 지정하지 않으면 전체 기간을 대상으로 합니다.
    """
    # 날짜 유효성 검사 추가 (선택적 파라미터이므로 둘 다 있을 때만 검사)
    if start_date and end_date and start_date > end_date:
         raise HTTPException(status_code=400, detail="시작 날짜는 종료 날짜보다 이전이어야 합니다.")

    map_summary_data = crud.get_map_summary(db=db, start_date=start_date, end_date=end_date)
    return schemas.MapSummaryResponse(
        start_date=start_date,
        end_date=end_date,
        summaries=map_summary_data
    )


@router.get("/summary/weekday", response_model=schemas.WeekdaySummaryResponse, tags=["Statistics - Profit"])
async def read_weekday_summary(
    start_date: Optional[datetime.date] = Query(None, description="조회 시작 날짜 (YYYY-MM-DD, 선택 사항)"),
    end_date: Optional[datetime.date] = Query(None, description="조회 종료 날짜 (YYYY-MM-DD, 선택 사항)"),
    db: Session = Depends(database.get_db)
):
    """
    요일별 수익 통계를 조회합니다. 기간을 지정하지 않으면 전체 기간을 대상으로 합니다.
    """
    # 날짜 유효성 검사 추가 (선택적 파라미터이므로 둘 다 있을 때만 검사)
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=400, detail="시작 날짜는 종료 날짜보다 이전이어야 합니다.")

    weekday_summary_data = crud.get_weekday_summary(db=db, start_date=start_date, end_date=end_date)
    return schemas.WeekdaySummaryResponse(
        start_date=start_date,
        end_date=end_date,
        summaries=weekday_summary_data
    )

# --- ⭐ 새로운 경험치 통계 엔드포인트 ---
@router.get("/experience/daily", response_model=schemas.DailyExperienceSummaryResponse, tags=["Statistics - Experience"])
async def read_daily_experience_summary(
    start_date: datetime.date = Query(..., description="조회 시작 날짜 (YYYY-MM-DD)"),
    end_date: datetime.date = Query(..., description="조회 종료 날짜 (YYYY-MM-DD)"),
    db: Session = Depends(database.get_db)
):
    """
    지정된 기간 동안의 일별 경험치 요약 통계를 조회합니다.
    - 사냥 기록만을 대상으로 합니다.
    - 시간당 평균 경험치는 해당 날짜의 총 사냥 시간이 0보다 클 때만 유효한 값으로 계산됩니다.
    """
    # 날짜 유효성 검사 추가
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="시작 날짜는 종료 날짜보다 이전이어야 합니다.")

    daily_summaries_data = crud.get_daily_experience_summary(db=db, start_date=start_date, end_date=end_date)

    # DailyExperienceSummaryResponse 스키마에 맞게 응답 데이터 구성
    return schemas.DailyExperienceSummaryResponse(
        start_date=start_date,
        end_date=end_date,
        summaries=daily_summaries_data
    )

# =========================================
# Auto-complete Data Endpoints
# =========================================

@router.get("/map-names/unique", response_model=List[str], tags=["Autocomplete Data"])
async def get_unique_map_names(db: Session = Depends(database.get_db)):
    """
    데이터베이스에 기록된 모든 고유한 맵 이름 목록을 반환합니다. (사냥, 쩔 기록 포함)
    자동 완성을 위해 사용됩니다.
    """
    return crud.get_unique_map_names(db)

@router.get("/rare-item-names/unique", response_model=List[str], tags=["Autocomplete Data"])
async def get_unique_rare_item_names(db: Session = Depends(database.get_db)):
    """
    데이터베이스에 기록된 모든 고유한 고가 아이템 이름 목록을 반환합니다. (사냥, 쩔 기록 포함)
    자동 완성을 위해 사용됩니다.
    """
    return crud.get_unique_rare_item_names(db)

@router.get("/consumable-item-names/unique", response_model=List[str], tags=["Autocomplete Data"])
async def get_unique_consumable_item_names(db: Session = Depends(database.get_db)):
    """
    데이터베이스에 기록된 모든 고유한 소모/기타 아이템 이름 목록을 반환합니다. (사냥, 쩔 기록 포함)
    자동 완성을 위해 사용됩니다.
    """
    return crud.get_unique_consumable_item_names(db)