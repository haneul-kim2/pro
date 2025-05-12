# C:\pro\app\crud.py (전체 수정본)

# -*- coding: utf-8 -*-
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, cast, Date as SQLDateType, Time, Integer as SQLInteger # SQLDateType으로 변경 (Python의 Date와 구분)
from . import models, schemas # models, schemas 제대로 import
import datetime
from typing import List, Dict, Tuple, Optional, Union # 필요한 typing 요소

# ================== ✨ 경험치 테이블 및 계산 함수 (파일 상단으로 이동) ✨ ==================
# '메이플랜드' 최종 레벨별 요구 경험치 (2024-08-XX 사용자 직접 제공 데이터 - 74->75 수정됨)
FINAL_MAPLELAND_EXP_TABLE = {
    # ... (이전에 제공한 전체 경험치 테이블 내용 그대로 복사) ...
    1: 15, 2: 34, 3: 57, 4: 92, 5: 135, 6: 372, 7: 560, 8: 840, 9: 1242,
    10: 1716, 11: 2360, 12: 3216, 13: 4200, 14: 5460, 15: 7050, 16: 8840, 17: 11040, 18: 13716, 19: 16680,
    20: 20216, 21: 24402, 22: 28980, 23: 34320, 24: 40512, 25: 54900, 26: 57210, 27: 63666, 28: 73080, 29: 83270,
    30: 95700, 31: 108480, 32: 122760, 33: 138666, 34: 155540, 35: 174216, 36: 194832, 37: 216600, 38: 240550, 39: 266682,
    40: 294216, 41: 324240, 42: 356916, 43: 391160, 44: 428280, 45: 468450, 46: 510420, 47: 555680, 48: 604416, 49: 655200,
    50: 709716, 51: 748608, 52: 789631, 53: 832902, 54: 878545, 55: 926689, 56: 977471, 57: 1031036, 58: 1087536, 59: 1147132,
    60: 1209904, 61: 1276301, 62: 1346242, 63: 1420016, 64: 1497832, 65: 1579913, 66: 1666492, 67: 1757185, 68: 1854143, 69: 1955750,
    70: 2062925, 71: 2175973, 72: 2295216, 73: 2420993, 74: 2553663, 75: 2693603, 76: 2841212, 77: 2996910, 78: 3161140, 79: 3334370,
    80: 3517903, 81: 3709827, 82: 3913127, 83: 4127556, 84: 4353756, 85: 4592341, 86: 4844001, 87: 5109452, 88: 5389449, 89: 5684790,
    90: 5996316, 91: 6324914, 92: 6617519, 93: 7037118, 94: 7422752, 95: 7829518, 96: 8258575, 97: 8711144, 98: 9188514, 99: 9620440,
    100: 10223168, 101: 10783397, 102: 11374327, 103: 11997640, 104: 12655575, 105: 13348610, 106: 14080113, 107: 14851703, 108: 15665676, 109: 16524049,
    110: 17429556, 111: 18384706, 112: 19392187, 113: 20454878, 114: 21575805, 115: 22758159, 116: 24005306, 117: 25320796, 118: 26708375, 119: 28171993,
    120: 29715818, 121: 31344244, 122: 33061908, 123: 34873700, 124: 36784778, 125: 38800583, 126: 40926854, 127: 43169645, 128: 45535341, 129: 48030677,
    130: 50662758, 131: 53439077, 132: 56367538, 133: 59456479, 134: 62714694, 135: 66151459, 136: 69776558, 137: 73600313, 138: 77633610, 139: 81887931,
    140: 86375389, 141: 91108760, 142: 96101520, 143: 101367883, 144: 106922842, 145: 112782213, 146: 118962678, 147: 125481832, 148: 132358236, 149: 139611467,
    150: 147262175, 151: 155332142, 152: 163844343, 153: 172823102, 154: 182293713, 155: 192283408, 156: 202820583, 157: 213935103, 158: 225658746, 159: 238024845,
    160: 251068606, 161: 264827165, 162: 289339693, 163: 294647508, 164: 310794191, 165: 327825712, 166: 345790561, 167: 364729883, 168: 384727628, 169: 405810702,
    170: 428049128, 171: 451506220, 172: 476248760, 173: 502347192, 174: 529875818, 175: 558913012, 176: 589531012, 177: 621848316, 178: 655925603, 179: 691870326,
    180: 729784819, 181: 769777027, 182: 811960808, 183: 856456260, 184: 903390063, 185: 952895838, 186: 1005114529, 187: 1060194805, 188: 1118293480, 189: 1179575962,
    190: 1244216724, 191: 1312399800, 192: 1384319309, 193: 1469180007, 194: 1540197371, 195: 1624600724, 196: 1713628833, 197: 1807535693, 198: 1906588643, 199: 2011069705
}

def calculate_gained_exp(
    start_level: int,
    start_exp_percentage: float,
    end_level: Optional[int],
    end_exp_percentage: Optional[float],
    exp_table: Dict[int, int] = FINAL_MAPLELAND_EXP_TABLE
) -> Union[int, None]:
    if end_level is None or end_exp_percentage is None:
        return None
    if start_level >= end_level and start_exp_percentage >= end_exp_percentage:
        if start_level == end_level and start_exp_percentage > end_exp_percentage:
            return 0
        return 0

    start_ratio = start_exp_percentage / 100.0
    end_ratio = end_exp_percentage / 100.0
    total_gained_exp = 0

    try:
        if start_level == end_level:
            required_exp = exp_table.get(start_level)
            if required_exp is None: return None
            gained_in_level = required_exp * (end_ratio - start_ratio)
            total_gained_exp = int(gained_in_level)
        elif start_level < end_level:
            required_exp_start_level = exp_table.get(start_level)
            if required_exp_start_level is None: return None
            exp_to_level_up = required_exp_start_level * (1.0 - start_ratio)
            total_gained_exp += int(exp_to_level_up)
            for level in range(start_level + 1, end_level):
                required_exp_intermediate = exp_table.get(level)
                if required_exp_intermediate is None: return None
                total_gained_exp += required_exp_intermediate
            required_exp_end_level = exp_table.get(end_level)
            if required_exp_end_level is None and end_level == max(exp_table.keys()) + 1:
                 required_exp_end_level = exp_table.get(end_level - 1)
            elif required_exp_end_level is None: return None
            exp_in_end_level = required_exp_end_level * end_ratio
            total_gained_exp += int(exp_in_end_level)
        if total_gained_exp < 0: total_gained_exp = 0
        return total_gained_exp
    except Exception as e:
        print(f"경험치 계산 중 오류 발생: {e}")
        return None
# =================================================================================

# =========================================
# Helper 함수: 시간 계산
# =========================================
def calculate_duration_minutes(start_dt: Optional[datetime.datetime], end_dt: Optional[datetime.datetime]) -> Optional[int]:
    """
    두 datetime 객체 사이의 시간을 분 단위로 계산합니다.
    하나라도 None이면 None을 반환합니다.
    종료 시간이 시작 시간보다 이르면 (자정을 넘긴 경우) 종료 시간에 하루를 더해 계산합니다.
    """
    if not start_dt or not end_dt:
        return None
    if end_dt < start_dt: # 자정 넘김 처리
        end_dt += datetime.timedelta(days=1)
    duration_delta = end_dt - start_dt
    return max(0, int(duration_delta.total_seconds() / 60)) # 음수 방지

# =========================================
# Hunting Session CRUD
# =========================================
def get_hunting_session(db: Session, log_id: int): # 함수명 변경 get_hunting_session_log -> get_hunting_session
    return db.query(models.HuntingSessionLog).filter(models.HuntingSessionLog.id == log_id).first()

def get_hunting_sessions(db: Session, skip: int = 0, limit: int = 100): # 함수명 변경 get_hunting_session_logs -> get_hunting_sessions
    # session_date 필드 기준으로 정렬 (models.py 에 session_date 필드가 있다고 가정)
    return db.query(models.HuntingSessionLog).order_by(models.HuntingSessionLog.session_date.desc(), models.HuntingSessionLog.start_time.desc()).offset(skip).limit(limit).all()

def create_hunting_session(db: Session, session: schemas.HuntingSessionCreate): # 함수명 변경 create_hunting_session_log -> create_hunting_session
    start_dt: Union[datetime.datetime, None] = None
    end_dt: Union[datetime.datetime, None] = None

    try:
        # models.py 에 session_date 가 있으므로 session.date 사용
        if session.date and session.start_time:
            start_hour, start_minute = map(int, session.start_time.split(':'))
            start_dt = datetime.datetime.combine(session.date, datetime.time(hour=start_hour, minute=start_minute))
        if session.date and session.end_time:
            end_hour, end_minute = map(int, session.end_time.split(':'))
            end_date_for_dt = session.date
            if start_dt and datetime.time(hour=end_hour, minute=end_minute) < start_dt.time():
                 end_date_for_dt += datetime.timedelta(days=1)
            end_dt = datetime.datetime.combine(end_date_for_dt, datetime.time(hour=end_hour, minute=end_minute))
    except Exception as e:
        print(f"Warning: 시간 결합 중 오류 발생 - {e}")

    duration = calculate_duration_minutes(start_dt, end_dt)

    calculated_gained_exp = calculate_gained_exp(
        start_level=session.start_level,
        start_exp_percentage=session.start_exp_percentage,
        end_level=session.end_level,
        end_exp_percentage=session.end_exp_percentage
    )

    # models.py의 필드명에 맞게 수정 (예: session_date, total_rare_item_value 등)
    db_session = models.HuntingSessionLog(
        session_date=session.date, # ✨ models.py의 session_date 필드 사용 ✨
        map_name=session.map_name,
        start_time=session.start_time, # ✨ 문자열 그대로 저장 (models.py가 String 타입이므로) ✨
        end_time=session.end_time,     # ✨ 문자열 그대로 저장 (models.py가 String 타입이므로) ✨
        duration_minutes=duration,
        start_level=session.start_level,
        start_exp_percentage=session.start_exp_percentage,
        end_level=session.end_level,
        end_exp_percentage=session.end_exp_percentage,
        gained_exp=calculated_gained_exp,
        start_meso=session.start_meso,
        end_meso=session.end_meso,
        sold_meso=getattr(session, 'sold_meso', 0), # sold_meso는 스키마에 없을 수 있음
        coupon_15min_count=session.coupon_used_count, # 필드명 coupon_used_count -> coupon_15min_count
        start_experience=session.start_experience,
        end_experience=session.end_experience,
        entry_fee=session.entry_fee,
        hunting_meso_profit=session.hunting_meso_profit,
        normal_item_profit=session.normal_item_profit,
        total_rare_item_value=session.rare_items_value, # 필드명 rare_items_value -> total_rare_item_value
        total_consumable_cost=session.consumable_cost, # 필드명 consumable_cost -> total_consumable_cost
        total_consumable_gained_profit=session.consumable_gain_value, # 필드명 consumable_gain_value -> total_consumable_gained_profit
        total_profit=session.total_profit,
        net_profit=session.net_profit,
        experience_profit=session.experience_profit,
        base_experience_profit=session.base_experience_profit,
        # character_name은 models.py에 없으므로 주석 처리 (또는 models.py에 추가)
        rare_items_detail=session.rare_items_detail, # 스키마에 있는 필드명 사용
        consumable_items_detail=session.consumable_items_detail # 스키마에 있는 필드명 사용
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

# =========================================
# Jjul Session CRUD (기존 내용 유지하되, 필드명 등 확인 필요)
# =========================================
def get_jjul_session(db: Session, log_id: int):
    return db.query(models.JjulSessionLog).filter(models.JjulSessionLog.id == log_id).first()

def get_jjul_sessions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.JjulSessionLog).order_by(models.JjulSessionLog.session_date.desc(), models.JjulSessionLog.start_time.desc()).offset(skip).limit(limit).all()

def create_jjul_session(db: Session, session: schemas.JjulSessionCreate):
    # 시간 처리 로직 추가 (HuntingSession과 유사하게)
    start_dt: Union[datetime.datetime, None] = None
    end_dt: Union[datetime.datetime, None] = None
    duration: Union[int, None] = None
    try:
        if session.date and session.start_time:
            start_hour, start_minute = map(int, session.start_time.split(':'))
            start_dt = datetime.datetime.combine(session.date, datetime.time(hour=start_hour, minute=start_minute))
        if session.date and session.end_time:
            end_hour, end_minute = map(int, session.end_time.split(':'))
            end_date_for_dt = session.date
            if start_dt and datetime.time(hour=end_hour, minute=end_minute) < start_dt.time():
                 end_date_for_dt += datetime.timedelta(days=1)
            end_dt = datetime.datetime.combine(end_date_for_dt, datetime.time(hour=end_hour, minute=end_minute))
        duration = calculate_duration_minutes(start_dt, end_dt)
    except Exception as e:
        print(f"Warning: Jjul 시간 결합 중 오류 발생 - {e}")

    db_session = models.JjulSessionLog(
        session_date=session.date, # models.py 필드명 사용
        map_name=session.map_name,
        start_time=session.start_time, # 문자열 그대로 저장 (models.py가 String 타입)
        end_time=session.end_time,     # 문자열 그대로 저장 (models.py가 String 타입)
        duration_minutes=duration,   # ✨ duration_minutes 추가 (models.py 에도 추가 필요) ✨
        start_meso=session.start_meso,
        end_meso=session.end_meso,
        sold_meso=getattr(session, 'sold_meso', 0), # 스키마에 sold_meso가 있는지 확인
        party_size=session.party_members_count, # 필드명 party_members_count -> party_size
        price_per_person=session.price_per_member, # 필드명 price_per_member -> price_per_person
        total_jjul_fee=session.total_jjul_fee,
        total_rare_item_value=session.rare_items_value, # 필드명 rare_items_value -> total_rare_item_value
        total_consumable_cost=session.consumable_cost,  # consumable_cost -> total_consumable_cost
        total_consumable_gained_profit=session.consumable_gain_value, # consumable_gain_value -> total_consumable_gained_profit
        normal_item_profit=session.normal_item_profit,
        total_profit=session.total_profit,
        net_profit=session.net_profit,
        rare_items_detail=session.rare_items_detail,
        consumable_items_detail=session.consumable_items_detail
        # character_name은 models.py에 없으므로 주석 처리 (또는 models.py에 추가)
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

# =========================================
# Meso Sale CRUD (기존 내용 유지하되, 필드명 등 확인 필요)
# =========================================
def get_meso_sale(db: Session, log_id: int):
    return db.query(models.MesoSaleLog).filter(models.MesoSaleLog.id == log_id).first()

def get_meso_sales(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.MesoSaleLog).order_by(models.MesoSaleLog.sale_date.desc()).offset(skip).limit(limit).all() # models.py의 sale_date 필드 사용

def create_meso_sale(db: Session, sale: schemas.MesoSaleCreate):
    db_sale = models.MesoSaleLog(
        sale_date=sale.date, # models.py 필드명 사용
        price_per_1m_meso=sale.price_per_1m, # models.py 필드명 사용
        quantity_sold_in_1m_units=sale.quantity_millions, # models.py 필드명 사용
        total_sale_amount_krw=sale.total_krw # models.py 필드명 사용
    )
    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)
    return db_sale

# =========================================
# Statistics CRUD (기존 수익 관련 - 필드명 등 models.py 기준으로 수정 필요)
# =========================================
def get_daily_summary(db: Session, start_date: datetime.date, end_date: datetime.date) -> List[schemas.DailySummaryItem]:
    hunting_summary = db.query(
        models.HuntingSessionLog.session_date.label("date"), # session_date 사용
        func.sum(models.HuntingSessionLog.hunting_meso_profit).label("total_hunting_meso"),
        func.sum(models.HuntingSessionLog.total_rare_item_value).label("total_rare_item_profit"), # total_rare_item_value 사용
        func.sum(models.HuntingSessionLog.normal_item_profit).label("total_normal_item_profit"),
        func.sum(models.HuntingSessionLog.total_consumable_gained_profit).label("total_consumable_gained"), # total_consumable_gained_profit 사용
        func.sum(models.HuntingSessionLog.total_consumable_cost).label("total_consumable_cost"), # total_consumable_cost 사용
        func.sum(models.HuntingSessionLog.entry_fee).label("total_entry_fee"),
        func.sum(models.HuntingSessionLog.total_profit).label("total_profit"),
        func.sum(models.HuntingSessionLog.net_profit).label("total_net_profit")
    ).filter(
        models.HuntingSessionLog.session_date >= start_date, # session_date 사용
        models.HuntingSessionLog.session_date <= end_date   # session_date 사용
    ).group_by(models.HuntingSessionLog.session_date).all()

    jjul_summary = db.query(
        models.JjulSessionLog.session_date.label("date"), # session_date 사용
        func.sum(models.JjulSessionLog.total_jjul_fee).label("total_jjul_profit"),
        func.sum(models.JjulSessionLog.total_rare_item_value).label("total_rare_item_profit"), # total_rare_item_value 사용
        func.sum(models.JjulSessionLog.normal_item_profit).label("total_normal_item_profit"),
        func.sum(models.JjulSessionLog.total_consumable_gained_profit).label("total_consumable_gained"), # total_consumable_gained_profit 사용
        func.sum(models.JjulSessionLog.total_consumable_cost).label("total_consumable_cost"), # total_consumable_cost 사용
        func.sum(models.JjulSessionLog.total_profit).label("total_profit"),
        func.sum(models.JjulSessionLog.net_profit).label("total_net_profit")
    ).filter(
        models.JjulSessionLog.session_date >= start_date, # session_date 사용
        models.JjulSessionLog.session_date <= end_date   # session_date 사용
    ).group_by(models.JjulSessionLog.session_date).all()

    meso_sale_summary = db.query(
        models.MesoSaleLog.sale_date.label("date"), # sale_date 사용
        func.sum(models.MesoSaleLog.total_sale_amount_krw).label("total_cash_sold") # total_sale_amount_krw 사용
    ).filter(
        models.MesoSaleLog.sale_date >= start_date, # sale_date 사용
        models.MesoSaleLog.sale_date <= end_date   # sale_date 사용
    ).group_by(models.MesoSaleLog.sale_date).all()

    summary_dict: Dict[datetime.date, Dict] = {}
    # (이하 병합 로직은 필드명 변경에 따라 data 딕셔너리 키값들 수정 필요)
    # ... (기존 병합 로직 유지, 단 data["..."] 접근 시 올바른 필드명 사용) ...
    for row in hunting_summary:
        date_key = row.date
        if date_key not in summary_dict: summary_dict[date_key] = {"hunting_meso": 0, "jjul_profit": 0, "rare_item_profit": 0, "normal_item_profit": 0, "consumable_gained": 0, "consumable_cost": 0, "entry_fee": 0, "cash_sold": 0}
        summary_dict[date_key]["hunting_meso"] += row.total_hunting_meso or 0
        summary_dict[date_key]["rare_item_profit"] += row.total_rare_item_profit or 0
        summary_dict[date_key]["normal_item_profit"] += row.total_normal_item_profit or 0
        summary_dict[date_key]["consumable_gained"] += row.total_consumable_gained or 0
        summary_dict[date_key]["consumable_cost"] += row.total_consumable_cost or 0
        summary_dict[date_key]["entry_fee"] += row.total_entry_fee or 0

    for row in jjul_summary:
        date_key = row.date
        if date_key not in summary_dict: summary_dict[date_key] = {"hunting_meso": 0, "jjul_profit": 0, "rare_item_profit": 0, "normal_item_profit": 0, "consumable_gained": 0, "consumable_cost": 0, "entry_fee": 0, "cash_sold": 0}
        summary_dict[date_key]["jjul_profit"] += row.total_jjul_profit or 0
        summary_dict[date_key]["rare_item_profit"] += row.total_rare_item_profit or 0
        summary_dict[date_key]["normal_item_profit"] += row.total_normal_item_profit or 0
        summary_dict[date_key]["consumable_gained"] += row.total_consumable_gained or 0
        summary_dict[date_key]["consumable_cost"] += row.total_consumable_cost or 0

    for row in meso_sale_summary:
        date_key = row.date
        if date_key not in summary_dict: summary_dict[date_key] = {"hunting_meso": 0, "jjul_profit": 0, "rare_item_profit": 0, "normal_item_profit": 0, "consumable_gained": 0, "consumable_cost": 0, "entry_fee": 0, "cash_sold": 0}
        summary_dict[date_key]["cash_sold"] += row.total_cash_sold or 0

    result_list: List[schemas.DailySummaryItem] = []
    for date_key, data in summary_dict.items():
        total_profit = data["hunting_meso"] + data["jjul_profit"] + data["rare_item_profit"] + data["normal_item_profit"] + data["consumable_gained"]
        net_profit = total_profit - data["consumable_cost"] - data["entry_fee"]
        result_list.append(schemas.DailySummaryItem(
            date=date_key,
            hunting_meso=data["hunting_meso"],
            jjul_profit=data["jjul_profit"],
            rare_item_profit=data["rare_item_profit"],
            normal_item_profit=data["normal_item_profit"],
            consumable_gained_profit=data["consumable_gained"], # 스키마 필드명 확인
            consumable_cost=data["consumable_cost"],
            entry_fee=data["entry_fee"],
            total_profit=total_profit,
            net_profit=net_profit,
            cash_sold_krw=data["cash_sold"]
        ))
    result_list.sort(key=lambda x: x.date)
    return result_list


def get_map_summary(db: Session, start_date: Optional[datetime.date] = None, end_date: Optional[datetime.date] = None) -> List[schemas.MapSummaryItem]:
    hunting_query = db.query(
        models.HuntingSessionLog.map_name,
        func.count(models.HuntingSessionLog.id).label("hunt_count"),
        func.sum(models.HuntingSessionLog.total_profit).label("total_hunt_profit"),
        func.sum(models.HuntingSessionLog.total_rare_item_value).label("total_rare_profit"), # total_rare_item_value 사용
        func.sum(models.HuntingSessionLog.total_consumable_gained_profit).label("total_consumable_gained") # total_consumable_gained_profit 사용
    )
    jjul_query = db.query(
        models.JjulSessionLog.map_name,
        func.count(models.JjulSessionLog.id).label("jjul_count"),
        func.sum(models.JjulSessionLog.total_profit).label("total_jjul_profit"),
        func.sum(models.JjulSessionLog.total_rare_item_value).label("total_rare_profit"), # total_rare_item_value 사용
        func.sum(models.JjulSessionLog.total_consumable_gained_profit).label("total_consumable_gained") # total_consumable_gained_profit 사용
    )
    if start_date:
        hunting_query = hunting_query.filter(models.HuntingSessionLog.session_date >= start_date) # session_date 사용
        jjul_query = jjul_query.filter(models.JjulSessionLog.session_date >= start_date)   # session_date 사용
    if end_date:
        hunting_query = hunting_query.filter(models.HuntingSessionLog.session_date <= end_date) # session_date 사용
        jjul_query = jjul_query.filter(models.JjulSessionLog.session_date <= end_date)   # session_date 사용

    hunting_summary = hunting_query.group_by(models.HuntingSessionLog.map_name).all()
    jjul_summary = jjul_query.group_by(models.JjulSessionLog.map_name).all()

    map_dict: Dict[str, Dict] = {}
    # ... (병합 로직은 필드명 변경에 따라 data 딕셔너리 키값들 수정 필요) ...
    # (기존 병합 로직 유지, 단 data["..."] 접근 시 올바른 필드명 사용)
    for row in hunting_summary:
        map_name_key = row.map_name
        if map_name_key not in map_dict: map_dict[map_name_key] = {"hunt_count": 0, "jjul_count": 0, "total_hunt_profit": 0, "total_jjul_profit": 0, "total_rare_profit": 0, "total_consumable_gained": 0}
        map_dict[map_name_key]["hunt_count"] += row.hunt_count or 0
        map_dict[map_name_key]["total_hunt_profit"] += row.total_hunt_profit or 0
        map_dict[map_name_key]["total_rare_profit"] += row.total_rare_profit or 0
        map_dict[map_name_key]["total_consumable_gained"] += row.total_consumable_gained or 0

    for row in jjul_summary:
        map_name_key = row.map_name
        if map_name_key not in map_dict: map_dict[map_name_key] = {"hunt_count": 0, "jjul_count": 0, "total_hunt_profit": 0, "total_jjul_profit": 0, "total_rare_profit": 0, "total_consumable_gained": 0}
        map_dict[map_name_key]["jjul_count"] += row.jjul_count or 0
        map_dict[map_name_key]["total_jjul_profit"] += row.total_jjul_profit or 0
        map_dict[map_name_key]["total_rare_profit"] += row.total_rare_profit or 0
        map_dict[map_name_key]["total_consumable_gained"] += row.total_consumable_gained or 0

    result_list: List[schemas.MapSummaryItem] = []
    for map_name_key, data in map_dict.items():
        total_profit_for_avg_hunt = data["total_hunt_profit"] + data["total_rare_profit"] + data["total_consumable_gained"]
        total_profit_for_avg_jjul = data["total_jjul_profit"] + data["total_rare_profit"] + data["total_consumable_gained"]
        avg_hunt_profit = (total_profit_for_avg_hunt / data["hunt_count"]) if data["hunt_count"] > 0 else 0
        avg_jjul_profit = (total_profit_for_avg_jjul / data["jjul_count"]) if data["jjul_count"] > 0 else 0
        result_list.append(schemas.MapSummaryItem(
            map_name=map_name_key,
            hunt_count=data["hunt_count"],
            jjul_count=data["jjul_count"],
            total_hunt_profit=data["total_hunt_profit"],
            total_jjul_profit=data["total_jjul_profit"],
            total_rare_item_profit=data["total_rare_profit"],
            total_consumable_gained_profit=data["total_consumable_gained"], # 스키마 필드명 확인
            average_hunt_profit=int(avg_hunt_profit),
            average_jjul_profit=int(avg_jjul_profit)
        ))
    result_list.sort(key=lambda x: (x.hunt_count + x.jjul_count), reverse=True)
    return result_list


def get_weekday_summary(db: Session, start_date: Optional[datetime.date] = None, end_date: Optional[datetime.date] = None) -> List[schemas.WeekdaySummaryItem]:
    weekday_map = { 0: "일요일", 1: "월요일", 2: "화요일", 3: "수요일", 4: "목요일", 5: "금요일", 6: "토요일" }
    weekday_func_hunt = cast(func.strftime('%w', models.HuntingSessionLog.session_date), SQLInteger) # session_date 사용
    weekday_func_jjul = cast(func.strftime('%w', models.JjulSessionLog.session_date), SQLInteger)   # session_date 사용

    hunting_query = db.query(
        weekday_func_hunt.label("weekday_num"),
        func.sum(models.HuntingSessionLog.hunting_meso_profit).label("hunting_profit"),
        func.sum(models.HuntingSessionLog.total_rare_item_value).label("rare_profit"),         # total_rare_item_value
        func.sum(models.HuntingSessionLog.normal_item_profit).label("normal_profit"),
        func.sum(models.HuntingSessionLog.total_consumable_gained_profit).label("consumable_gained"), # total_consumable_gained_profit
        func.sum(models.HuntingSessionLog.net_profit).label("net_profit")
    )
    jjul_query = db.query(
        weekday_func_jjul.label("weekday_num"),
        func.sum(models.JjulSessionLog.total_jjul_fee).label("jjul_profit"),
        func.sum(models.JjulSessionLog.total_rare_item_value).label("rare_profit"),         # total_rare_item_value
        func.sum(models.JjulSessionLog.normal_item_profit).label("normal_profit"),
        func.sum(models.JjulSessionLog.total_consumable_gained_profit).label("consumable_gained"), # total_consumable_gained_profit
        func.sum(models.JjulSessionLog.net_profit).label("net_profit")
    )
    if start_date:
        hunting_query = hunting_query.filter(models.HuntingSessionLog.session_date >= start_date) # session_date 사용
        jjul_query = jjul_query.filter(models.JjulSessionLog.session_date >= start_date)   # session_date 사용
    if end_date:
        hunting_query = hunting_query.filter(models.HuntingSessionLog.session_date <= end_date) # session_date 사용
        jjul_query = jjul_query.filter(models.JjulSessionLog.session_date <= end_date)   # session_date 사용

    hunting_summary = hunting_query.group_by("weekday_num").all()
    jjul_summary = jjul_query.group_by("weekday_num").all()

    weekday_dict: Dict[int, Dict] = {i: {"weekday_name": name, "hunting_profit": 0, "jjul_profit": 0, "rare_profit": 0, "normal_profit": 0, "consumable_gained": 0, "net_profit": 0} for i, name in weekday_map.items()}
    # ... (병합 로직은 필드명 변경에 따라 data 딕셔너리 키값들 수정 필요) ...
    # (기존 병합 로직 유지, 단 data["..."] 접근 시 올바른 필드명 사용)
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
            consumable_gained_profit=data["consumable_gained"], # 스키마 필드명 확인
            total_profit=total_profit,
            net_profit=data["net_profit"]
        ))
    result_list.sort(key=lambda x: list(weekday_map.values()).index(x.weekday_name))
    return result_list

# =========================================
# Unique Names CRUD (기존 내용 유지)
# =========================================
def get_unique_map_names(db: Session) -> List[str]:
    hunting_maps = db.query(models.HuntingSessionLog.map_name).distinct().all()
    jjul_maps = db.query(models.JjulSessionLog.map_name).distinct().all()
    unique_names = sorted(list(set([m[0] for m in hunting_maps if m[0]] + [m[0] for m in jjul_maps if m[0]])))
    return unique_names

def get_unique_rare_item_names(db: Session) -> List[str]:
    hunting_items = db.query(models.HuntingSessionLog.rare_items_detail).filter(models.HuntingSessionLog.rare_items_detail != None).all()
    jjul_items = db.query(models.JjulSessionLog.rare_items_detail).filter(models.JjulSessionLog.rare_items_detail != None).all()
    names = set()
    import json
    for item_detail_json in hunting_items + jjul_items:
        try:
            items = json.loads(item_detail_json[0])
            for item in items:
                if 'name' in item and item['name']:
                    names.add(item['name'])
        except (json.JSONDecodeError, TypeError, IndexError): continue
    return sorted(list(names))

def get_unique_consumable_item_names(db: Session) -> List[str]:
    hunting_items = db.query(models.HuntingSessionLog.consumable_items_detail).filter(models.HuntingSessionLog.consumable_items_detail != None).all()
    jjul_items = db.query(models.JjulSessionLog.consumable_items_detail).filter(models.JjulSessionLog.consumable_items_detail != None).all()
    names = set()
    import json
    for item_detail_json in hunting_items + jjul_items:
        try:
            items = json.loads(item_detail_json[0])
            for item in items:
                 if 'name' in item and item['name']:
                    names.add(item['name'])
        except (json.JSONDecodeError, TypeError, IndexError): continue
    return sorted(list(names))

# =========================================
# ⭐ 신규 CRUD 함수: 일별 경험치 요약 (기존 experience_profit 기반) ⭐
# =========================================
def get_daily_experience_summary(db: Session, start_date: datetime.date, end_date: datetime.date) -> List[schemas.DailyExperienceSummaryItem]:
    logs = db.query(
        models.HuntingSessionLog.session_date.label("date"), # session_date 사용
        models.HuntingSessionLog.start_time,
        models.HuntingSessionLog.end_time,
        models.HuntingSessionLog.experience_profit,
        models.HuntingSessionLog.base_experience_profit,
        models.HuntingSessionLog.duration_minutes # ✨ duration_minutes 직접 사용 ✨
    ).filter(
        models.HuntingSessionLog.session_date >= start_date, # session_date 사용
        models.HuntingSessionLog.session_date <= end_date,  # session_date 사용
        models.HuntingSessionLog.experience_profit != None,
        models.HuntingSessionLog.base_experience_profit != None
    ).order_by(models.HuntingSessionLog.session_date).all()

    daily_summaries: Dict[datetime.date, Dict] = {}
    for log in logs:
        log_date = log.date
        if log_date not in daily_summaries:
            daily_summaries[log_date] = {
                "total_session_count": 0, "total_duration_minutes": 0,
                "total_experience_profit": 0, "total_base_experience_profit": 0,
            }
        # duration_minutes가 None이 아니고 0보다 클 때만 합산
        current_duration = log.duration_minutes if log.duration_minutes is not None else 0
        if current_duration > 0:
            daily_summaries[log_date]["total_duration_minutes"] += current_duration

        daily_summaries[log_date]["total_session_count"] += 1
        daily_summaries[log_date]["total_experience_profit"] += log.experience_profit or 0
        daily_summaries[log_date]["total_base_experience_profit"] += log.base_experience_profit or 0

    result_list: List[schemas.DailyExperienceSummaryItem] = []
    for date_key, summary in daily_summaries.items():
        total_duration_minutes = summary["total_duration_minutes"]
        avg_exp_per_hour = 0.0
        avg_base_exp_per_hour = 0.0
        if total_duration_minutes > 0:
            total_duration_hours = total_duration_minutes / 60.0
            avg_exp_per_hour = round(summary["total_experience_profit"] / total_duration_hours, 2)
            avg_base_exp_per_hour = round(summary["total_base_experience_profit"] / total_duration_hours, 2)
        summary_item = schemas.DailyExperienceSummaryItem(
            date=date_key, total_session_count=summary["total_session_count"],
            total_duration_minutes=total_duration_minutes,
            total_experience_profit=summary["total_experience_profit"],
            total_base_experience_profit=summary["total_base_experience_profit"],
            average_experience_per_hour=avg_exp_per_hour,
            average_base_experience_per_hour=avg_base_exp_per_hour,
        )
        result_list.append(summary_item)
    result_list.sort(key=lambda item: item.date)
    return result_list

# ================== ✨ gained_exp 기반 통계 함수 (v2) - 신규 추가 ✨ ==================
def get_average_exp_per_hour_v2(db: Session) -> float:
    results = db.query(
        func.sum(models.HuntingSessionLog.gained_exp).label("total_exp"),
        func.sum(models.HuntingSessionLog.duration_minutes).label("total_minutes")
    ).filter(
        models.HuntingSessionLog.gained_exp.isnot(None),
        models.HuntingSessionLog.duration_minutes.isnot(None),
        models.HuntingSessionLog.duration_minutes > 0
    ).first()
    if results and results.total_minutes and results.total_minutes > 0 and results.total_exp is not None:
        try:
            avg_exp_per_minute = results.total_exp / results.total_minutes
            return avg_exp_per_minute * 60
        except ZeroDivisionError: return 0.0
    else: return 0.0

def get_daily_total_exp_v2(db: Session, start_date: Optional[datetime.date] = None, end_date: Optional[datetime.date] = None) -> Dict[str, int]:
    query = db.query(
        func.date(models.HuntingSessionLog.start_time).label("date"), # ✨ start_time을 기준으로 날짜 추출 (models.py의 DateTime 필드 사용)✨
        func.sum(models.HuntingSessionLog.gained_exp).label("daily_total_exp")
    ).filter(
        models.HuntingSessionLog.start_time.isnot(None), # ✨ start_time 필드 사용 ✨
        models.HuntingSessionLog.gained_exp.isnot(None),
        models.HuntingSessionLog.gained_exp > 0
    )
    if start_date:
        start_datetime = datetime.datetime.combine(start_date, datetime.time.min)
        query = query.filter(models.HuntingSessionLog.start_time >= start_datetime) # ✨ start_time 필드 사용 ✨
    if end_date:
        end_datetime = datetime.datetime.combine(end_date + datetime.timedelta(days=1), datetime.time.min)
        query = query.filter(models.HuntingSessionLog.start_time < end_datetime) # ✨ start_time 필드 사용 ✨

    query = query.group_by(func.date(models.HuntingSessionLog.start_time)).order_by(func.date(models.HuntingSessionLog.start_time)) # ✨ start_time 필드 사용 ✨
    results = query.all()
    daily_exp_dict = {result.date.isoformat(): (result.daily_total_exp if result.daily_total_exp is not None else 0) for result in results if result.date}
    return daily_exp_dict
# =======================================================================