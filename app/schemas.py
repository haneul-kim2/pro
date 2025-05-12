# C:\pro\app\schemas.py (전체 수정본)

# -*- coding: utf-8 -*-
from pydantic import BaseModel, Field, ConfigDict # ConfigDict 추가
from typing import List, Optional, Any, Dict, Union
import datetime # datetime 추가
from datetime import date # date는 이미 있음

# =========================================
# Hunting Session Schemas
# =========================================
class HuntingSessionBase(BaseModel):
    # character_name: str # models.py에 character_name이 있다면 주석 해제
    session_date: date # models.py 필드명 session_date 사용 (스키마에서는 date로 받아도 무방)
    map_name: str
    start_time: Union[str, None] = None # HH:MM 형식 문자열
    end_time: Union[str, None] = None   # HH:MM 형식 문자열
    # duration_minutes: Optional[int] = None # ✨ 조회 시 사용, 생성 시에는 자동 계산되므로 Base에선 제외 가능 ✨

    start_level: int
    start_exp_percentage: float = Field(..., ge=0.0, le=100.0) # 필수, 0~100
    end_level: Optional[int] = None
    end_exp_percentage: Optional[float] = Field(None, ge=0.0, le=100.0) # 선택, 0~100

    start_meso: int = 0
    end_meso: int = 0
    sold_meso: int = 0 # models.py 필드명 사용
    coupon_15min_count: int = 0 # models.py 필드명 사용 (coupon_used_count -> coupon_15min_count)
    start_experience: float = 0 # models.py 타입 Float
    end_experience: float = 0   # models.py 타입 Float
    entry_fee: int = 0
    # 아래 수익/비용 필드들은 스키마에서 직접 받기보다, create 시 계산하는 것이 좋을 수 있음
    # 또는 사용자가 직접 입력하도록 둘 수도 있음 (현재 로직 유지)
    hunting_meso_profit: int = 0
    normal_item_profit: int = 0
    total_rare_item_value: int = 0 # models.py 필드명 사용
    total_consumable_cost: int = 0 # models.py 필드명 사용
    total_consumable_gained_profit: int = 0 # models.py 필드명 사용
    total_profit: int = 0
    net_profit: int = 0
    experience_profit: float = 0   # models.py 타입 Float
    base_experience_profit: float = 0 # models.py 타입 Float
    rare_items_detail: Union[str, None] = None
    consumable_items_detail: Union[str, None] = None


class HuntingSessionCreate(HuntingSessionBase):
    # Base의 모든 필드를 상속받아 사용
    pass

class HuntingSession(HuntingSessionBase): # 조회용 스키마 (기존 HuntingSessionLog 역할)
    id: int
    duration_minutes: Optional[int] = None # ✨ 추가된 필드 (조회 시 필요) ✨
    gained_exp: Optional[int] = None       # ✨ 추가된 필드 (조회 시 필요) ✨

    model_config = ConfigDict(from_attributes=True) # Pydantic V2


# =========================================
# Jjul Session Schemas
# =========================================
class JjulSessionBase(BaseModel):
    # character_name: str # models.py에 character_name이 있다면 주석 해제
    session_date: date # models.py 필드명 사용
    map_name: str
    start_time: Union[str, None] = None
    end_time: Union[str, None] = None
    # duration_minutes: Optional[int] = None # ✨ 조회 시 사용 ✨

    start_meso: int = 0
    end_meso: int = 0
    sold_meso: int = 0 # models.py 필드명 사용
    party_size: int = 0 # models.py 필드명 사용
    price_per_person: int = 0 # models.py 필드명 사용
    total_jjul_fee: int = 0
    total_rare_item_value: int = 0 # models.py 필드명 사용
    total_consumable_cost: int = 0 # models.py 필드명 사용
    total_consumable_gained_profit: int = 0 # models.py 필드명 사용
    normal_item_profit: int = 0
    total_profit: int = 0
    net_profit: int = 0
    rare_items_detail: Union[str, None] = None
    consumable_items_detail: Union[str, None] = None

class JjulSessionCreate(JjulSessionBase):
    pass

class JjulSession(JjulSessionBase): # 조회용 스키마
    id: int
    duration_minutes: Optional[int] = None # ✨ 추가된 필드 (조회 시 필요) ✨

    model_config = ConfigDict(from_attributes=True)


# =========================================
# Meso Sale Schemas
# =========================================
class MesoSaleBase(BaseModel):
    sale_date: date # models.py 필드명 사용
    price_per_1m_meso: int # models.py 필드명 사용
    quantity_sold_in_1m_units: float # models.py 필드명 사용

class MesoSaleCreate(MesoSaleBase):
    total_sale_amount_krw: int # models.py 필드명 사용

class MesoSale(MesoSaleBase):
    id: int
    total_sale_amount_krw: int # models.py 필드명 사용

    model_config = ConfigDict(from_attributes=True)


# =========================================
# Statistics Schemas
# =========================================
class DailySummaryItem(BaseModel):
    date: date # Python의 date 타입 사용
    hunting_meso: int = 0
    jjul_profit: int = 0
    rare_item_profit: int = 0
    normal_item_profit: int = 0
    consumable_gained_profit: int = 0
    consumable_cost: int = 0
    entry_fee: int = 0 # 사냥에서만 발생
    total_profit: int = 0
    net_profit: int = 0
    cash_sold_krw: int = 0 # 메소 판매 수익

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
    total_rare_item_profit: int = 0 # 해당 맵에서 발생한 총 고가템 수익
    total_consumable_gained_profit: int = 0 # 해당 맵에서 발생한 총 소모템 획득 수익
    average_hunt_profit: int = 0 # 정수형으로 Tkinter 버전과 통일
    average_jjul_profit: int = 0 # 정수형으로 Tkinter 버전과 통일

    model_config = ConfigDict(from_attributes=True)

class MapSummaryResponse(BaseModel):
    start_date: Union[date, None] = None # Optional이므로 Union 사용
    end_date: Union[date, None] = None   # Optional이므로 Union 사용
    summaries: List[MapSummaryItem]

    model_config = ConfigDict(from_attributes=True)

class WeekdaySummaryItem(BaseModel):
    weekday_name: str # "월요일", "화요일" 등
    hunting_profit: int = 0
    jjul_profit: int = 0
    rare_item_profit: int = 0
    normal_item_profit: int = 0
    consumable_gained_profit: int = 0
    total_profit: int = 0 # 해당 요일의 모든 활동 총 수익
    net_profit: int = 0   # 해당 요일의 모든 활동 순수익

    model_config = ConfigDict(from_attributes=True)

class WeekdaySummaryResponse(BaseModel):
    start_date: Union[date, None] = None
    end_date: Union[date, None] = None
    summaries: List[WeekdaySummaryItem]

    model_config = ConfigDict(from_attributes=True)

# --- 경험치 통계 스키마 ---
class DailyExperienceSummaryItem(BaseModel):
    date: date
    total_session_count: int
    total_duration_minutes: int
    total_experience_profit: float # models.py 와 타입 일치 (Float)
    total_base_experience_profit: float # models.py 와 타입 일치 (Float)
    average_experience_per_hour: float
    average_base_experience_per_hour: float

    model_config = ConfigDict(from_attributes=True)

class DailyExperienceSummaryResponse(BaseModel):
    start_date: date
    end_date: date
    summaries: List[DailyExperienceSummaryItem]

    model_config = ConfigDict(from_attributes=True)

# 시간당 평균 경험치 통계 스키마 (gained_exp 기반 v2)
class ExpAverageStats(BaseModel):
    average_exp_per_hour: float

# 일별 총 경험치 통계 스키마 (gained_exp 기반 v2)
class ExpDailyStats(BaseModel):
    daily_exp: Dict[str, int] # Key: "YYYY-MM-DD"