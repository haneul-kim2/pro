# -*- coding: utf-8 -*-
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Any, Dict, Union # Union 추가
import datetime
from datetime import date

# =========================================
# Hunting Session Schemas
# =========================================
class HuntingSessionBase(BaseModel):
    # 기본 타입 필드는 Field 없이 선언 시도
    date: date
    map_name: str
    # Optional 필드는 Union과 default=None 사용 시도
    start_time: Union[str, None] = None # pattern 제거
    end_time: Union[str, None] = None   # pattern 제거
    start_meso: int = 0
    end_meso: int = 0
    meso_after_sell: int = 0
    rare_items_value: int = 0
    coupon_used_count: int = 0
    start_experience: int = 0
    end_experience: int = 0
    consumable_cost: int = 0
    consumable_gain_value: int = 0
    entry_fee: int = 0
    rare_items_detail: Union[str, None] = None
    consumable_items_detail: Union[str, None] = None

# ... (나머지 스키마들은 일단 유지) ...
# (단, 동일한 패턴으로 수정해야 할 수도 있음)

class HuntingSessionCreate(HuntingSessionBase):
    hunting_meso_profit: int = 0
    normal_item_profit: int = 0
    total_profit: int = 0
    net_profit: int = 0
    experience_profit: int = 0
    base_experience_profit: int = 0
    rare_items: Union[str, None] = None

class HuntingSession(HuntingSessionBase):
    id: int
    hunting_meso_profit: int
    normal_item_profit: int
    total_profit: int
    net_profit: int
    experience_profit: int
    base_experience_profit: int
    rare_items: Union[str, None] = None

    model_config = ConfigDict(
        from_attributes=True,
    )

# =========================================
# Jjul Session Schemas (동일 패턴 적용)
# =========================================
class JjulSessionBase(BaseModel):
    date: date
    map_name: str
    start_time: Union[str, None] = None # pattern 제거
    end_time: Union[str, None] = None   # pattern 제거
    start_meso: int = 0
    end_meso: int = 0
    meso_after_sell: int = 0
    party_members_count: int = 0
    price_per_member: int = 0
    rare_items_value: int = 0
    consumable_cost: int = 0
    consumable_gain_value: int = 0
    rare_items_detail: Union[str, None] = None
    consumable_items_detail: Union[str, None] = None

class JjulSessionCreate(JjulSessionBase):
    total_jjul_fee: int = 0
    normal_item_profit: int = 0
    total_profit: int = 0
    net_profit: int = 0
    rare_items: Union[str, None] = None

class JjulSession(JjulSessionBase):
    id: int
    total_jjul_fee: int
    normal_item_profit: int
    total_profit: int
    net_profit: int
    rare_items: Union[str, None] = None

    model_config = ConfigDict(
        from_attributes=True,
    )

# =========================================
# Meso Sale Schemas (Field 제약조건 제거 시도)
# =========================================
class MesoSaleBase(BaseModel):
    date: date
    price_per_1m: int # gt=0 제거
    quantity_millions: float # gt=0 제거

class MesoSaleCreate(MesoSaleBase):
    total_krw: int

class MesoSale(MesoSaleBase):
    id: int
    total_krw: int

    model_config = ConfigDict(
        from_attributes=True,
    )

# =========================================
# Statistics Schemas (기본값 위주로 단순화)
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

    model_config = ConfigDict(
        from_attributes=True,
    )

class DailySummaryResponse(BaseModel):
    start_date: date
    end_date: date
    summaries: List[DailySummaryItem]

    model_config = ConfigDict(
        from_attributes=True,
    )

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

    model_config = ConfigDict(
        from_attributes=True,
    )

class MapSummaryResponse(BaseModel):
    start_date: Union[date, None] = None
    end_date: Union[date, None] = None
    summaries: List[MapSummaryItem]

    model_config = ConfigDict(
        from_attributes=True,
    )

class WeekdaySummaryItem(BaseModel):
    weekday_name: str
    hunting_profit: int = 0
    jjul_profit: int = 0
    rare_item_profit: int = 0
    normal_item_profit: int = 0
    consumable_gained_profit: int = 0
    total_profit: int = 0
    net_profit: int = 0

    model_config = ConfigDict(
        from_attributes=True,
    )

class WeekdaySummaryResponse(BaseModel):
    start_date: Union[date, None] = None
    end_date: Union[date, None] = None
    summaries: List[WeekdaySummaryItem]

    model_config = ConfigDict(
        from_attributes=True,
    )

# --- 경험치 통계 스키마 (단순화 시도) ---
class DailyExperienceSummaryItem(BaseModel):
    date: date
    total_session_count: int
    total_duration_minutes: int
    total_experience_profit: int
    total_base_experience_profit: int
    average_experience_per_hour: float
    average_base_experience_per_hour: float

    model_config = ConfigDict(
        from_attributes=True,
    )

class DailyExperienceSummaryResponse(BaseModel):
    start_date: date
    end_date: date
    summaries: List[DailyExperienceSummaryItem]

    model_config = ConfigDict(
        from_attributes=True,
    )