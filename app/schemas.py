# schemas.py 파일 상단에 필요한 import 문 확인 (이미 있다면 중복 추가 X)
# -*- coding: utf-8 -*-
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Any, Dict, Union
import datetime
from datetime import date

# =========================================
# Hunting Session Schemas
# =========================================
class HuntingSessionBase(BaseModel):
    session_date: date
    map_name: str
    start_time: Union[str, None] = None
    end_time: Union[str, None] = None

    start_level: int
    start_exp_percentage: float = Field(..., ge=0.0, le=100.0)
    end_level: Optional[int] = None
    end_exp_percentage: Optional[float] = Field(None, ge=0.0, le=100.0)

    start_meso: int = 0
    end_meso: int = 0
    sold_meso: int = 0
    coupon_15min_count: int = 0
    entry_fee: int = 0
    hunting_meso_profit: int = 0
    normal_item_profit: int = 0
    total_rare_item_value: int = 0
    total_consumable_cost: int = 0
    total_consumable_gained_profit: int = 0
    total_profit: int = 0
    net_profit: int = 0
    rare_items_detail: Union[str, None] = None
    consumable_items_detail: Union[str, None] = None

class HuntingSessionCreate(HuntingSessionBase):
    pass

class HuntingSession(HuntingSessionBase):
    id: int
    duration_minutes: Optional[int] = None
    gained_exp: Optional[int] = None 
    base_experience_profit: Optional[float] = None
    created_at: Optional[datetime.datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


# =========================================
# Jjul Session Schemas
# =========================================
class JjulSessionBase(BaseModel):
    session_date: date
    map_name: str
    start_time: Union[str, None] = None
    end_time: Union[str, None] = None

    start_meso: int = 0
    end_meso: int = 0
    sold_meso: int = 0
    party_size: int = 0
    price_per_person: int = 0
    total_jjul_fee: int = 0
    total_rare_item_value: int = 0
    total_consumable_cost: int = 0
    total_consumable_gained_profit: int = 0
    normal_item_profit: int = 0
    total_profit: int = 0
    net_profit: int = 0
    rare_items_detail: Union[str, None] = None
    consumable_items_detail: Union[str, None] = None

class JjulSessionCreate(JjulSessionBase):
    pass

class JjulSession(JjulSessionBase):
    id: int
    duration_minutes: Optional[int] = None
    created_at: Optional[datetime.datetime] = None

    model_config = ConfigDict(from_attributes=True)


# =========================================
# Meso Sale Schemas
# =========================================
class MesoSaleBase(BaseModel):
    sale_date: date
    price_per_1m_meso: int
    quantity_sold_in_1m_units: float

class MesoSaleCreate(MesoSaleBase):
    total_sale_amount_krw: int

class MesoSale(MesoSaleBase):
    id: int
    total_sale_amount_krw: int
    created_at: Optional[datetime.datetime] = None

    model_config = ConfigDict(from_attributes=True)


# =========================================
# Statistics Schemas (Profit)
# =========================================
class DailySummaryItem(BaseModel):
    date: date
    hunting_meso: int = 0
    jjul_profit: int = 0
    rare_item_profit: int = 0
    normal_item_profit: int = 0
    consumable_gained_profit: int = 0
    consumable_cost: int = 0
    entry_fee: int = 0
    total_profit: int = 0
    net_profit: int = 0
    cash_sold_krw: int = 0

    model_config = ConfigDict(from_attributes=True)

class DailySummaryResponse(BaseModel):
    start_date: date
    end_date: date
    summaries: List[DailySummaryItem]

    model_config = ConfigDict(from_attributes=True)

class MapSummaryItem(BaseModel):
    map_name: str
    hunt_count: int = 0
    jjul_count: int = 0
    total_hunt_profit: int = 0
    total_jjul_profit: int = 0
    total_rare_item_profit: int = 0
    total_consumable_gained_profit: int = 0
    average_hunt_profit: int = 0
    average_jjul_profit: int = 0

    model_config = ConfigDict(from_attributes=True)

class MapSummaryResponse(BaseModel):
    start_date: Union[date, None] = None
    end_date: Union[date, None] = None
    summaries: List[MapSummaryItem]

    model_config = ConfigDict(from_attributes=True)

class WeekdaySummaryItem(BaseModel):
    weekday_name: str
    hunting_profit: int = 0
    jjul_profit: int = 0
    rare_item_profit: int = 0
    normal_item_profit: int = 0
    consumable_gained_profit: int = 0
    total_profit: int = 0
    net_profit: int = 0

    model_config = ConfigDict(from_attributes=True)

class WeekdaySummaryResponse(BaseModel):
    start_date: Union[date, None] = None
    end_date: Union[date, None] = None
    summaries: List[WeekdaySummaryItem]

    model_config = ConfigDict(from_attributes=True)

# =========================================
# Statistics Schemas (Experience - General)
# =========================================
class DailyExperienceSummaryItem(BaseModel): # 일별 경험치 요약 (기존, 상세 항목 포함)
    date: date
    total_session_count: int
    total_duration_minutes: int
    total_experience_profit: float # gained_exp 총합
    total_base_experience_profit: float # base_experience_profit 총합
    average_experience_per_hour: float
    average_base_experience_per_hour: float

    model_config = ConfigDict(from_attributes=True)

class DailyExperienceSummaryResponse(BaseModel):
    start_date: date
    end_date: date
    summaries: List[DailyExperienceSummaryItem]

    model_config = ConfigDict(from_attributes=True)

class ExpAverageStats(BaseModel): # 전체 기간 시간당 평균 경험치
    average_exp_per_hour: float
    model_config = ConfigDict(from_attributes=True)

class DailyExpValues(BaseModel): # 일별 상세 경험치 값 (gained_exp, base_exp)
    gained_exp: int
    base_exp: Optional[float] = None
    model_config = ConfigDict(from_attributes=True)

class ExpDailyStats(BaseModel): # 일별 상세 경험치 응답 (v2)
    daily_exp: Dict[date, DailyExpValues]
    model_config = ConfigDict(from_attributes=True)


# =========================================
# Statistics Schemas (Experience - Weekday & Map)
# =========================================

# --- 요일별 경험치 요약 스키마 ---
class ExperienceWeekdaySummaryItem(BaseModel):
    """요일별 경험치 요약 항목 (개별 요일 데이터)"""
    weekday_name: str
    total_gained_exp: int = 0
    total_duration_minutes: int = 0
    session_count: int = 0
    average_exp_per_hour: float = 0.0

    model_config = ConfigDict(from_attributes=True)


class ExperienceWeekdaySummaryResponse(BaseModel):
    """요일별 경험치 요약 API 응답 전체 구조"""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    summaries: List[ExperienceWeekdaySummaryItem]

    model_config = ConfigDict(from_attributes=True)

# --- 맵별 경험치 요약 스키마 (신규 추가) ---
class ExperienceMapSummaryItem(BaseModel):
    """맵별 경험치 요약 항목 (개별 맵 데이터)"""
    map_name: str  # 사냥터 맵 이름
    total_gained_exp: int = 0  # 해당 맵에서 획득한 총 경험치 (사냥 기록 기반)
    total_duration_minutes: int = 0  # 해당 맵에서의 총 사냥 시간 (분)
    session_count: int = 0  # 해당 맵에서 기록된 사냥 세션 수
    average_exp_per_hour: float = 0.0  # 해당 맵에서의 시간당 평균 획득 경험치
    # (선택적) average_exp_per_session: float = 0.0 # 세션당 평균 획득 경험치

    model_config = ConfigDict(from_attributes=True)


class ExperienceMapSummaryResponse(BaseModel):
    """맵별 경험치 요약 API 응답 전체 구조"""
    start_date: Optional[date] = None  # 조회 시작 날짜
    end_date: Optional[date] = None    # 조회 종료 날짜
    summaries: List[ExperienceMapSummaryItem]  # 맵별 요약 데이터 리스트

    model_config = ConfigDict(from_attributes=True)

# =========================================
# Generic Response Schemas
# =========================================
class DeleteResponse(BaseModel):
    message: str
    deleted_id: Optional[int] = None
    deleted_count: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)