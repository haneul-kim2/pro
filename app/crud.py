# -*- coding: utf-8 -*-
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, cast, Date, Time, Integer # 필요한 SQLAlchemy 함수 및 타입 추가/확인
from . import models, schemas
import datetime
from typing import List, Dict, Tuple, Optional # 필요한 typing 요소 추가/확인

# =========================================
# Helper 함수: 시간 계산
# =========================================
def calculate_duration_minutes(start_dt: datetime.datetime, end_dt: datetime.datetime) -> int:
    """
    두 datetime 객체 사이의 시간을 분 단위로 계산합니다.
    종료 시간이 시작 시간보다 이르면 (자정을 넘긴 경우) 종료 시간에 하루를 더해 계산합니다.
    """
    if end_dt < start_dt:
        end_dt += datetime.timedelta(days=1)
    duration = end_dt - start_dt
    # 총 초를 60으로 나누어 분 단위로 변환하고 정수형으로 반환
    return int(duration.total_seconds() / 60)

# =========================================
# Hunting Session CRUD
# =========================================
def get_hunting_session(db: Session, log_id: int):
    return db.query(models.HuntingSessionLog).filter(models.HuntingSessionLog.id == log_id).first()

def get_hunting_sessions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.HuntingSessionLog).order_by(models.HuntingSessionLog.date.desc(), models.HuntingSessionLog.start_time.desc()).offset(skip).limit(limit).all()

def create_hunting_session(db: Session, session: schemas.HuntingSessionCreate):
    # 시간 문자열을 time 객체로 변환 (데이터베이스 저장을 위해)
    start_time_obj = datetime.datetime.strptime(session.start_time, "%H:%M").time() if session.start_time else None
    end_time_obj = datetime.datetime.strptime(session.end_time, "%H:%M").time() if session.end_time else None

    db_session = models.HuntingSessionLog(
        date=session.date,
        map_name=session.map_name,
        start_time=start_time_obj,
        end_time=end_time_obj,
        start_meso=session.start_meso,
        end_meso=session.end_meso,
        meso_after_sell=session.meso_after_sell,
        rare_items=session.rare_items,
        rare_items_value=session.rare_items_value,
        coupon_used_count=session.coupon_used_count,
        start_experience=session.start_experience,
        end_experience=session.end_experience,
        consumable_cost=session.consumable_cost,
        consumable_gain_value=session.consumable_gain_value,
        entry_fee=session.entry_fee,
        hunting_meso_profit=session.hunting_meso_profit,
        normal_item_profit=session.normal_item_profit,
        total_profit=session.total_profit,
        net_profit=session.net_profit,
        experience_profit=session.experience_profit,
        base_experience_profit=session.base_experience_profit,
        # 동적 아이템 목록 데이터 처리 (문자열 결합 또는 JSON 등으로 저장)
        rare_items_detail=session.rare_items_detail,
        consumable_items_detail=session.consumable_items_detail
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

# =========================================
# Jjul Session CRUD
# =========================================
def get_jjul_session(db: Session, log_id: int):
    return db.query(models.JjulSessionLog).filter(models.JjulSessionLog.id == log_id).first()

def get_jjul_sessions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.JjulSessionLog).order_by(models.JjulSessionLog.date.desc(), models.JjulSessionLog.start_time.desc()).offset(skip).limit(limit).all()

def create_jjul_session(db: Session, session: schemas.JjulSessionCreate):
    start_time_obj = datetime.datetime.strptime(session.start_time, "%H:%M").time() if session.start_time else None
    end_time_obj = datetime.datetime.strptime(session.end_time, "%H:%M").time() if session.end_time else None

    db_session = models.JjulSessionLog(
        date=session.date,
        map_name=session.map_name,
        start_time=start_time_obj,
        end_time=end_time_obj,
        start_meso=session.start_meso,
        end_meso=session.end_meso,
        meso_after_sell=session.meso_after_sell,
        party_members_count=session.party_members_count,
        price_per_member=session.price_per_member,
        total_jjul_fee=session.total_jjul_fee,
        rare_items=session.rare_items,
        rare_items_value=session.rare_items_value,
        consumable_cost=session.consumable_cost,
        consumable_gain_value=session.consumable_gain_value,
        normal_item_profit=session.normal_item_profit,
        total_profit=session.total_profit,
        net_profit=session.net_profit,
        # 동적 아이템 목록 데이터 처리
        rare_items_detail=session.rare_items_detail,
        consumable_items_detail=session.consumable_items_detail
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

# =========================================
# Meso Sale CRUD
# =========================================
def get_meso_sale(db: Session, log_id: int):
    return db.query(models.MesoSaleLog).filter(models.MesoSaleLog.id == log_id).first()

def get_meso_sales(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.MesoSaleLog).order_by(models.MesoSaleLog.date.desc()).offset(skip).limit(limit).all()

def create_meso_sale(db: Session, sale: schemas.MesoSaleCreate):
    db_sale = models.MesoSaleLog(
        date=sale.date,
        price_per_1m=sale.price_per_1m,
        quantity_millions=sale.quantity_millions,
        total_krw=sale.total_krw
    )
    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)
    return db_sale

# =========================================
# Statistics CRUD (기존 수익 관련)
# =========================================
def get_daily_summary(db: Session, start_date: datetime.date, end_date: datetime.date) -> List[schemas.DailySummaryItem]:
    # 사냥 데이터 집계
    hunting_summary = db.query(
        models.HuntingSessionLog.date,
        func.sum(models.HuntingSessionLog.hunting_meso_profit).label("total_hunting_meso"),
        func.sum(models.HuntingSessionLog.rare_items_value).label("total_rare_item_profit"),
        func.sum(models.HuntingSessionLog.normal_item_profit).label("total_normal_item_profit"),
        func.sum(models.HuntingSessionLog.consumable_gain_value).label("total_consumable_gained"),
        func.sum(models.HuntingSessionLog.consumable_cost).label("total_consumable_cost"),
        func.sum(models.HuntingSessionLog.entry_fee).label("total_entry_fee"),
        func.sum(models.HuntingSessionLog.total_profit).label("total_profit"),
        func.sum(models.HuntingSessionLog.net_profit).label("total_net_profit")
    ).filter(
        models.HuntingSessionLog.date >= start_date,
        models.HuntingSessionLog.date <= end_date
    ).group_by(models.HuntingSessionLog.date).all()

    # 쩔 데이터 집계
    jjul_summary = db.query(
        models.JjulSessionLog.date,
        func.sum(models.JjulSessionLog.total_jjul_fee).label("total_jjul_profit"),
        func.sum(models.JjulSessionLog.rare_items_value).label("total_rare_item_profit"),
        func.sum(models.JjulSessionLog.normal_item_profit).label("total_normal_item_profit"),
        func.sum(models.JjulSessionLog.consumable_gain_value).label("total_consumable_gained"),
        func.sum(models.JjulSessionLog.consumable_cost).label("total_consumable_cost"),
        func.sum(models.JjulSessionLog.total_profit).label("total_profit"),
        func.sum(models.JjulSessionLog.net_profit).label("total_net_profit")
    ).filter(
        models.JjulSessionLog.date >= start_date,
        models.JjulSessionLog.date <= end_date
    ).group_by(models.JjulSessionLog.date).all()

    # 메소 판매 데이터 집계
    meso_sale_summary = db.query(
        models.MesoSaleLog.date,
        func.sum(models.MesoSaleLog.total_krw).label("total_cash_sold")
    ).filter(
        models.MesoSaleLog.date >= start_date,
        models.MesoSaleLog.date <= end_date
    ).group_by(models.MesoSaleLog.date).all()

    # 결과 병합 (Python으로 처리)
    summary_dict: Dict[datetime.date, Dict] = {}

    for row in hunting_summary:
        if row.date not in summary_dict: summary_dict[row.date] = {"hunting_meso": 0, "jjul_profit": 0, "rare_item_profit": 0, "normal_item_profit": 0, "consumable_gained": 0, "consumable_cost": 0, "entry_fee": 0, "cash_sold": 0}
        summary_dict[row.date]["hunting_meso"] += row.total_hunting_meso or 0
        summary_dict[row.date]["rare_item_profit"] += row.total_rare_item_profit or 0
        summary_dict[row.date]["normal_item_profit"] += row.total_normal_item_profit or 0
        summary_dict[row.date]["consumable_gained"] += row.total_consumable_gained or 0
        summary_dict[row.date]["consumable_cost"] += row.total_consumable_cost or 0
        summary_dict[row.date]["entry_fee"] += row.total_entry_fee or 0

    for row in jjul_summary:
        if row.date not in summary_dict: summary_dict[row.date] = {"hunting_meso": 0, "jjul_profit": 0, "rare_item_profit": 0, "normal_item_profit": 0, "consumable_gained": 0, "consumable_cost": 0, "entry_fee": 0, "cash_sold": 0}
        summary_dict[row.date]["jjul_profit"] += row.total_jjul_profit or 0
        summary_dict[row.date]["rare_item_profit"] += row.total_rare_item_profit or 0
        summary_dict[row.date]["normal_item_profit"] += row.total_normal_item_profit or 0
        summary_dict[row.date]["consumable_gained"] += row.total_consumable_gained or 0
        summary_dict[row.date]["consumable_cost"] += row.total_consumable_cost or 0
        # 쩔에는 지참비가 없음

    for row in meso_sale_summary:
        if row.date not in summary_dict: summary_dict[row.date] = {"hunting_meso": 0, "jjul_profit": 0, "rare_item_profit": 0, "normal_item_profit": 0, "consumable_gained": 0, "consumable_cost": 0, "entry_fee": 0, "cash_sold": 0}
        summary_dict[row.date]["cash_sold"] += row.total_cash_sold or 0

    result_list: List[schemas.DailySummaryItem] = []
    for date, data in summary_dict.items():
        total_profit = data["hunting_meso"] + data["jjul_profit"] + data["rare_item_profit"] + data["normal_item_profit"] + data["consumable_gained"]
        net_profit = total_profit - data["consumable_cost"] - data["entry_fee"] # 지참비는 사냥에서만 발생
        result_list.append(schemas.DailySummaryItem(
            date=date,
            hunting_meso=data["hunting_meso"],
            jjul_profit=data["jjul_profit"],
            rare_item_profit=data["rare_item_profit"],
            normal_item_profit=data["normal_item_profit"],
            consumable_gained_profit=data["consumable_gained"],
            consumable_cost=data["consumable_cost"],
            entry_fee=data["entry_fee"],
            total_profit=total_profit,
            net_profit=net_profit,
            cash_sold_krw=data["cash_sold"]
        ))

    result_list.sort(key=lambda x: x.date)
    return result_list


def get_map_summary(db: Session, start_date: Optional[datetime.date] = None, end_date: Optional[datetime.date] = None) -> List[schemas.MapSummaryItem]:
    # 사냥 맵별 집계
    hunting_query = db.query(
        models.HuntingSessionLog.map_name,
        func.count(models.HuntingSessionLog.id).label("hunt_count"),
        func.sum(models.HuntingSessionLog.total_profit).label("total_hunt_profit"), # 총수익 기준
        func.sum(models.HuntingSessionLog.rare_items_value).label("total_rare_profit"),
        func.sum(models.HuntingSessionLog.consumable_gain_value).label("total_consumable_gained")
    )
    # 쩔 맵별 집계
    jjul_query = db.query(
        models.JjulSessionLog.map_name,
        func.count(models.JjulSessionLog.id).label("jjul_count"),
        func.sum(models.JjulSessionLog.total_profit).label("total_jjul_profit"), # 총수익 기준
        func.sum(models.JjulSessionLog.rare_items_value).label("total_rare_profit"),
        func.sum(models.JjulSessionLog.consumable_gain_value).label("total_consumable_gained")
    )

    if start_date:
        hunting_query = hunting_query.filter(models.HuntingSessionLog.date >= start_date)
        jjul_query = jjul_query.filter(models.JjulSessionLog.date >= start_date)
    if end_date:
        hunting_query = hunting_query.filter(models.HuntingSessionLog.date <= end_date)
        jjul_query = jjul_query.filter(models.JjulSessionLog.date <= end_date)

    hunting_summary = hunting_query.group_by(models.HuntingSessionLog.map_name).all()
    jjul_summary = jjul_query.group_by(models.JjulSessionLog.map_name).all()

    # 결과 병합 (Python)
    map_dict: Dict[str, Dict] = {}

    for row in hunting_summary:
        if row.map_name not in map_dict: map_dict[row.map_name] = {"hunt_count": 0, "jjul_count": 0, "total_hunt_profit": 0, "total_jjul_profit": 0, "total_rare_profit": 0, "total_consumable_gained": 0}
        map_dict[row.map_name]["hunt_count"] += row.hunt_count or 0
        map_dict[row.map_name]["total_hunt_profit"] += row.total_hunt_profit or 0
        map_dict[row.map_name]["total_rare_profit"] += row.total_rare_profit or 0
        map_dict[row.map_name]["total_consumable_gained"] += row.total_consumable_gained or 0

    for row in jjul_summary:
        if row.map_name not in map_dict: map_dict[row.map_name] = {"hunt_count": 0, "jjul_count": 0, "total_hunt_profit": 0, "total_jjul_profit": 0, "total_rare_profit": 0, "total_consumable_gained": 0}
        map_dict[row.map_name]["jjul_count"] += row.jjul_count or 0
        map_dict[row.map_name]["total_jjul_profit"] += row.total_jjul_profit or 0
        map_dict[row.map_name]["total_rare_profit"] += row.total_rare_profit or 0 # 고가템 수익은 양쪽에 다 더함
        map_dict[row.map_name]["total_consumable_gained"] += row.total_consumable_gained or 0 # 소모템 획득 수익도 양쪽에 다 더함

    result_list: List[schemas.MapSummaryItem] = []
    for map_name, data in map_dict.items():
        # 평균 수익 계산 시, 해당 활동(사냥/쩔)의 총 수익과 해당 맵에서 발생한 '모든' 고가템/소모템획득 수익을 합산하여 횟수로 나눔 (Tkinter 버전 로직 준수)
        total_profit_for_avg_hunt = data["total_hunt_profit"] + data["total_rare_profit"] + data["total_consumable_gained"]
        total_profit_for_avg_jjul = data["total_jjul_profit"] + data["total_rare_profit"] + data["total_consumable_gained"]

        avg_hunt_profit = (total_profit_for_avg_hunt / data["hunt_count"]) if data["hunt_count"] > 0 else 0
        avg_jjul_profit = (total_profit_for_avg_jjul / data["jjul_count"]) if data["jjul_count"] > 0 else 0

        result_list.append(schemas.MapSummaryItem(
            map_name=map_name,
            hunt_count=data["hunt_count"],
            jjul_count=data["jjul_count"],
            total_hunt_profit=data["total_hunt_profit"],
            total_jjul_profit=data["total_jjul_profit"],
            total_rare_item_profit=data["total_rare_profit"],
            total_consumable_gained_profit=data["total_consumable_gained"],
            average_hunt_profit=int(avg_hunt_profit), # Tkinter 버전과 같이 정수형으로
            average_jjul_profit=int(avg_jjul_profit)  # Tkinter 버전과 같이 정수형으로
        ))

    result_list.sort(key=lambda x: (x.hunt_count + x.jjul_count), reverse=True) # 총 횟수 기준 내림차순 정렬
    return result_list


def get_weekday_summary(db: Session, start_date: Optional[datetime.date] = None, end_date: Optional[datetime.date] = None) -> List[schemas.WeekdaySummaryItem]:
    # 요일 이름 매핑 (0=월요일, ..., 6=일요일) - PostgreSQL 기준 (isodow), SQLite 기준 (strftime('%w')는 0=일요일) 주의
    weekday_map = {
        0: "일요일", 1: "월요일", 2: "화요일", 3: "수요일", 4: "목요일", 5: "금요일", 6: "토요일"
    } # SQLite strftime('%w') 기준

    # 데이터베이스 종류에 따라 요일 추출 함수 변경 필요
    # 예: PostgreSQL -> func.extract('isodow', models.HuntingSessionLog.date) - 1 (월요일 0부터 시작)
    # 예: SQLite -> cast(func.strftime('%w', models.HuntingSessionLog.date), Integer) (일요일 0부터 시작)
    weekday_func_hunt = cast(func.strftime('%w', models.HuntingSessionLog.date), Integer)
    weekday_func_jjul = cast(func.strftime('%w', models.JjulSessionLog.date), Integer)

    # 사냥 요일별 집계
    hunting_query = db.query(
        weekday_func_hunt.label("weekday_num"),
        func.sum(models.HuntingSessionLog.hunting_meso_profit).label("hunting_profit"), # 순수 사냥 메소 수익
        func.sum(models.HuntingSessionLog.rare_items_value).label("rare_profit"),
        func.sum(models.HuntingSessionLog.normal_item_profit).label("normal_profit"),
        func.sum(models.HuntingSessionLog.consumable_gain_value).label("consumable_gained"),
        func.sum(models.HuntingSessionLog.net_profit).label("net_profit")
    )
    # 쩔 요일별 집계
    jjul_query = db.query(
        weekday_func_jjul.label("weekday_num"),
        func.sum(models.JjulSessionLog.total_jjul_fee).label("jjul_profit"), # 순수 쩔비 수익
        func.sum(models.JjulSessionLog.rare_items_value).label("rare_profit"),
        func.sum(models.JjulSessionLog.normal_item_profit).label("normal_profit"),
        func.sum(models.JjulSessionLog.consumable_gain_value).label("consumable_gained"),
        func.sum(models.JjulSessionLog.net_profit).label("net_profit")
    )

    if start_date:
        hunting_query = hunting_query.filter(models.HuntingSessionLog.date >= start_date)
        jjul_query = jjul_query.filter(models.JjulSessionLog.date >= start_date)
    if end_date:
        hunting_query = hunting_query.filter(models.HuntingSessionLog.date <= end_date)
        jjul_query = jjul_query.filter(models.JjulSessionLog.date <= end_date)

    hunting_summary = hunting_query.group_by("weekday_num").all()
    jjul_summary = jjul_query.group_by("weekday_num").all()

    # 결과 병합 (Python)
    weekday_dict: Dict[int, Dict] = {i: {"weekday_name": name, "hunting_profit": 0, "jjul_profit": 0, "rare_profit": 0, "normal_profit": 0, "consumable_gained": 0, "net_profit": 0} for i, name in weekday_map.items()}

    for row in hunting_summary:
        if row.weekday_num in weekday_dict:
            weekday_dict[row.weekday_num]["hunting_profit"] += row.hunting_profit or 0
            weekday_dict[row.weekday_num]["rare_profit"] += row.rare_profit or 0
            weekday_dict[row.weekday_num]["normal_profit"] += row.normal_profit or 0
            weekday_dict[row.weekday_num]["consumable_gained"] += row.consumable_gained or 0
            weekday_dict[row.weekday_num]["net_profit"] += row.net_profit or 0

    for row in jjul_summary:
        if row.weekday_num in weekday_dict:
            weekday_dict[row.weekday_num]["jjul_profit"] += row.jjul_profit or 0
            weekday_dict[row.weekday_num]["rare_profit"] += row.rare_profit or 0
            weekday_dict[row.weekday_num]["normal_profit"] += row.normal_profit or 0
            weekday_dict[row.weekday_num]["consumable_gained"] += row.consumable_gained or 0
            weekday_dict[row.weekday_num]["net_profit"] += row.net_profit or 0

    result_list: List[schemas.WeekdaySummaryItem] = []
    for weekday_num, data in weekday_dict.items():
        total_profit = data["hunting_profit"] + data["jjul_profit"] + data["rare_profit"] + data["normal_profit"] + data["consumable_gained"]
        result_list.append(schemas.WeekdaySummaryItem(
            weekday_name=data["weekday_name"],
            hunting_profit=data["hunting_profit"],
            jjul_profit=data["jjul_profit"],
            rare_item_profit=data["rare_profit"],
            normal_item_profit=data["normal_profit"],
            consumable_gained_profit=data["consumable_gained"],
            total_profit=total_profit,
            net_profit=data["net_profit"] # 순수익은 각 레코드에서 계산된 값의 합
        ))

    # 요일 순서대로 정렬 (일, 월, 화, 수, 목, 금, 토)
    result_list.sort(key=lambda x: list(weekday_map.values()).index(x.weekday_name))
    return result_list

# =========================================
# Unique Names CRUD (자동 완성을 위함)
# =========================================
def get_unique_map_names(db: Session) -> List[str]:
    # 사냥과 쩔 양쪽에서 고유 맵 이름 가져오기
    hunting_maps = db.query(models.HuntingSessionLog.map_name).distinct().all()
    jjul_maps = db.query(models.JjulSessionLog.map_name).distinct().all()
    # 결과를 합치고 중복 제거 후 정렬
    unique_names = sorted(list(set([m[0] for m in hunting_maps if m[0]] + [m[0] for m in jjul_maps if m[0]])))
    return unique_names

def get_unique_rare_item_names(db: Session) -> List[str]:
    # 사냥과 쩔 양쪽에서 고유 고가 아이템 이름 가져오기
    # 'rare_items_detail' 필드는 JSON 문자열로 가정
    hunting_items = db.query(models.HuntingSessionLog.rare_items_detail).filter(models.HuntingSessionLog.rare_items_detail != None).all()
    jjul_items = db.query(models.JjulSessionLog.rare_items_detail).filter(models.JjulSessionLog.rare_items_detail != None).all()

    names = set()
    import json
    for item_detail_json in hunting_items + jjul_items:
        try:
            items = json.loads(item_detail_json[0]) # 튜플의 첫번째 요소가 JSON 문자열
            for item in items:
                if 'name' in item and item['name']:
                    names.add(item['name'])
        except (json.JSONDecodeError, TypeError, IndexError):
            # JSON 파싱 실패 또는 예상치 못한 형식은 무시
            continue

    return sorted(list(names))

def get_unique_consumable_item_names(db: Session) -> List[str]:
    # 사냥과 쩔 양쪽에서 고유 소모/기타 아이템 이름 가져오기
    # 'consumable_items_detail' 필드는 JSON 문자열로 가정
    hunting_items = db.query(models.HuntingSessionLog.consumable_items_detail).filter(models.HuntingSessionLog.consumable_items_detail != None).all()
    jjul_items = db.query(models.JjulSessionLog.consumable_items_detail).filter(models.JjulSessionLog.consumable_items_detail != None).all()

    names = set()
    import json
    for item_detail_json in hunting_items + jjul_items:
        try:
            items = json.loads(item_detail_json[0]) # 튜플의 첫번째 요소가 JSON 문자열
            for item in items:
                 if 'name' in item and item['name']:
                    names.add(item['name'])
        except (json.JSONDecodeError, TypeError, IndexError):
            # JSON 파싱 실패 또는 예상치 못한 형식은 무시
            continue

    return sorted(list(names))

# =========================================
# ⭐ 신규 CRUD 함수: 일별 경험치 요약 ⭐
# =========================================
def get_daily_experience_summary(db: Session, start_date: datetime.date, end_date: datetime.date) -> List[schemas.DailyExperienceSummaryItem]:
    """
    지정된 기간 동안의 일별 경험치 요약 데이터를 계산하여 리스트 형태로 반환합니다.
    """

    # 1. DB에서 해당 기간의 사냥 기록 조회 (필요 컬럼만 선택)
    #    시간 계산을 위해 date, start_time, end_time 필드가 필요합니다.
    logs = db.query(
        models.HuntingSessionLog.date,
        models.HuntingSessionLog.start_time,
        models.HuntingSessionLog.end_time,
        models.HuntingSessionLog.experience_profit,
        models.HuntingSessionLog.base_experience_profit
    ).filter(
        models.HuntingSessionLog.date >= start_date,
        models.HuntingSessionLog.date <= end_date,
        # 경험치 정보가 있는 기록만 대상으로 함 (None이 아닌 경우)
        models.HuntingSessionLog.experience_profit != None,
        models.HuntingSessionLog.base_experience_profit != None
    ).order_by(models.HuntingSessionLog.date).all() # 날짜순으로 정렬하여 조회

    # 2. Python Dictionary를 사용하여 날짜별 데이터 집계
    #    Key: 날짜(date), Value: 해당 날짜의 집계 정보 Dictionary
    daily_summaries: Dict[datetime.date, Dict] = {}

    for log in logs:
        log_date = log.date

        # 해당 날짜의 집계 정보가 없으면 초기화
        if log_date not in daily_summaries:
            daily_summaries[log_date] = {
                "total_session_count": 0,
                "total_duration_minutes": 0,
                "total_experience_profit": 0,
                "total_base_experience_profit": 0,
            }

        # 시간 계산 (start_time과 end_time이 모두 존재해야 함)
        duration_minutes = 0 # 기본값 0
        if log.start_time and log.end_time:
            try:
                # date 필드와 time 필드를 결합하여 datetime 객체 생성
                start_dt = datetime.datetime.combine(log_date, log.start_time)
                end_dt = datetime.datetime.combine(log_date, log.end_time)
                # 위에서 정의한 calculate_duration_minutes 함수 사용
                duration_minutes = calculate_duration_minutes(start_dt, end_dt)
                # 유효한 시간만 누적 (예: 0분 이하는 제외)
                if duration_minutes > 0:
                    daily_summaries[log_date]["total_duration_minutes"] += duration_minutes
                else:
                    # 시간이 0분이거나 음수면 세션 카운트만 증가 (선택적 처리)
                    print(f"Warning: Calculated duration is <= 0 for log on {log_date}. Duration: {duration_minutes} min. Not added to total duration.")
            except Exception as e:
                # 시간 변환 또는 계산 중 오류 발생 시 로그 기록 (선택적)
                print(f"Warning: Could not calculate duration for log on {log_date}. Error: {e}")
                # duration_minutes는 0으로 유지됨
        else:
             # 시작 또는 종료 시간이 없는 경우, 해당 로그의 시간은 0분으로 처리
             pass

        # 다른 값들 집계 (시간이 유효하게 계산되었을 때만 집계하는 것을 고려할 수 있음)
        # 현재 로직: 시간이 0이더라도 경험치는 집계
        daily_summaries[log_date]["total_session_count"] += 1
        daily_summaries[log_date]["total_experience_profit"] += log.experience_profit if log.experience_profit is not None else 0
        daily_summaries[log_date]["total_base_experience_profit"] += log.base_experience_profit if log.base_experience_profit is not None else 0

    # 3. 집계된 데이터를 DailyExperienceSummaryItem 스키마 리스트로 변환
    result_list: List[schemas.DailyExperienceSummaryItem] = []
    for date, summary in daily_summaries.items():
        total_duration_minutes = summary["total_duration_minutes"]
        avg_exp_per_hour = 0.0
        avg_base_exp_per_hour = 0.0

        # 시간당 평균 계산 (0으로 나누기 방지)
        if total_duration_minutes > 0:
            # 분 단위를 시간 단위로 변환 (total_duration_minutes / 60)
            total_duration_hours = total_duration_minutes / 60.0 # 부동소수점 나누기
            # 시간당 평균 경험치 계산 (소수점 2자리까지 반올림)
            avg_exp_per_hour = round(summary["total_experience_profit"] / total_duration_hours, 2)
            avg_base_exp_per_hour = round(summary["total_base_experience_profit"] / total_duration_hours, 2)

        # 스키마 객체 생성
        summary_item = schemas.DailyExperienceSummaryItem(
            date=date,
            total_session_count=summary["total_session_count"],
            total_duration_minutes=total_duration_minutes,
            total_experience_profit=summary["total_experience_profit"],
            total_base_experience_profit=summary["total_base_experience_profit"],
            average_experience_per_hour=avg_exp_per_hour,
            average_base_experience_per_hour=avg_base_exp_per_hour,
        )
        result_list.append(summary_item)

    # 날짜 순서대로 정렬 (이미 정렬된 상태로 조회했지만, 최종 결과 정렬 보장)
    result_list.sort(key=lambda item: item.date)

    return result_list

# =========================================
# (향후 추가될 CRUD 함수들)
# - 개별 기록 수정/삭제
# - 데이터 초기화 등
# =========================================