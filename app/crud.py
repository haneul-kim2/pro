# -*- coding: utf-8 -*-
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, cast, Date as SQLDateType, Time, Integer as SQLInteger 
from . import models, schemas 
import datetime
from typing import List, Dict, Tuple, Optional, Union 
import json # get_unique_... 함수들에서 사용

# ================== ✨ 경험치 테이블 및 계산 함수 (파일 상단으로 이동) ✨ ==================
# '메이플랜드' 최종 레벨별 요구 경험치 (2024-08-XX 사용자 직접 제공 데이터 - 74->75 수정됨)
FINAL_MAPLELAND_EXP_TABLE = {
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
    if start_level > end_level: 
        return 0 
    if start_level == end_level and start_exp_percentage >= end_exp_percentage:
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
            if required_exp_end_level is None and end_level == (max(exp_table.keys(), default=0) + 1):
                 required_exp_end_level = exp_table.get(end_level -1, 0) 
            elif required_exp_end_level is None:
                print(f"Warning: Level {end_level} not found in exp_table during calculation.")
                return None

            exp_in_end_level = required_exp_end_level * end_ratio
            total_gained_exp += int(exp_in_end_level)
            
        if total_gained_exp < 0: total_gained_exp = 0
        return total_gained_exp
    except Exception as e:
        print(f"경험치 계산 중 오류 발생: {e}")
        return None
# =================================================================================

# === ✨ 새로운 함수 추가 시작: 마지막 사냥/쩔 기록 조회 ✨ ===
def get_last_hunting_session(db: Session) -> Optional[models.HuntingSessionLog]:
    """가장 최근에 기록된 사냥 세션 로그를 반환합니다."""
    print("[DEBUG CRUD] Entered get_last_hunting_session")
    try:
        result = db.query(models.HuntingSessionLog)\
                 .order_by(models.HuntingSessionLog.session_date.desc(), models.HuntingSessionLog.id.desc())\
                 .first()
        if result:
            print(f"[DEBUG CRUD] get_last_hunting_session found: id={result.id}, map={result.map_name}")
        else:
            print("[DEBUG CRUD] get_last_hunting_session found no record (None).")
        return result
    except Exception as e:
        print(f"[DEBUG CRUD] Error in get_last_hunting_session: {e}")
        raise 

def get_last_jjul_session(db: Session) -> Optional[models.JjulSessionLog]:
    """가장 최근에 기록된 쩔 세션 로그를 반환합니다."""
    print("[DEBUG CRUD] Entered get_last_jjul_session")
    try:
        result = db.query(models.JjulSessionLog)\
                 .order_by(models.JjulSessionLog.session_date.desc(), models.JjulSessionLog.id.desc())\
                 .first()
        if result:
            print(f"[DEBUG CRUD] get_last_jjul_session found: id={result.id}, map={result.map_name}")
        else:
            print("[DEBUG CRUD] get_last_jjul_session found no record (None).")
        return result
    except Exception as e:
        print(f"[DEBUG CRUD] Error in get_last_jjul_session: {e}")
        raise
# === ✨ 새로운 함수 추가 끝 ✨ ===

# === ✨ 새로운 함수 추가 시작: 삭제 기능 ✨ ===
def delete_hunting_session(db: Session, log_id: int) -> bool:
    db_log = db.query(models.HuntingSessionLog).filter(models.HuntingSessionLog.id == log_id).first()
    if db_log: 
        db.delete(db_log)
        db.commit()
        return True
    return False

def delete_jjul_session(db: Session, log_id: int) -> bool:
    db_log = db.query(models.JjulSessionLog).filter(models.JjulSessionLog.id == log_id).first()
    if db_log: 
        db.delete(db_log)
        db.commit()
        return True
    return False

def delete_meso_sale(db: Session, log_id: int) -> bool:
    db_log = db.query(models.MesoSaleLog).filter(models.MesoSaleLog.id == log_id).first()
    if db_log: 
        db.delete(db_log)
        db.commit()
        return True
    return False

# --- 전체 기록 삭제 ---
def delete_all_hunting_sessions(db: Session) -> int:
    num_deleted = db.query(models.HuntingSessionLog).delete()
    db.commit()
    return num_deleted

def delete_all_jjul_sessions(db: Session) -> int:
    num_deleted = db.query(models.JjulSessionLog).delete()
    db.commit()
    return num_deleted

def delete_all_meso_sales(db: Session) -> int:
    num_deleted = db.query(models.MesoSaleLog).delete()
    db.commit()
    return num_deleted
# === ✨ 새로운 함수 추가 끝 ✨ ===


# =========================================
# Helper 함수: 시간 계산
# =========================================
def calculate_duration_minutes(start_dt: Optional[datetime.datetime], end_dt: Optional[datetime.datetime]) -> Optional[int]:
    if not start_dt or not end_dt:
        return None
    duration_delta = end_dt - start_dt
    return max(0, int(duration_delta.total_seconds() / 60))

# =========================================
# Hunting Session CRUD
# =========================================
def get_hunting_session(db: Session, log_id: int):
    return db.query(models.HuntingSessionLog).filter(models.HuntingSessionLog.id == log_id).first()

def get_hunting_sessions(db: Session, skip: int = 0, limit: int = 100, 
                         start_date: Optional[datetime.date] = None, 
                         end_date: Optional[datetime.date] = None,
                         map_name: Optional[str] = None):
    query = db.query(models.HuntingSessionLog)
    if start_date:
        query = query.filter(models.HuntingSessionLog.session_date >= start_date)
    if end_date:
        query = query.filter(models.HuntingSessionLog.session_date <= end_date)
    if map_name:
        query = query.filter(models.HuntingSessionLog.map_name == map_name)
        
    return query.order_by(
        models.HuntingSessionLog.session_date.desc(), 
        models.HuntingSessionLog.start_time.desc(),
        models.HuntingSessionLog.id.desc()
    ).offset(skip).limit(limit).all()


def create_hunting_session(db: Session, session: schemas.HuntingSessionCreate):
    start_dt: Union[datetime.datetime, None] = None
    end_dt: Union[datetime.datetime, None] = None
    print(f"\n[DEBUG CRUD] --- Starting create_hunting_session for map: {session.map_name} ---")

    try:
        if session.session_date and session.start_time:
            start_hour, start_minute = map(int, session.start_time.split(':'))
            start_dt = datetime.datetime.combine(session.session_date, datetime.time(hour=start_hour, minute=start_minute))
        
        if session.session_date and session.end_time:
            end_hour, end_minute = map(int, session.end_time.split(':'))
            end_date_for_dt = session.session_date 
            if start_dt and datetime.time(hour=end_hour, minute=end_minute) < start_dt.time():
                end_date_for_dt += datetime.timedelta(days=1)
            end_dt = datetime.datetime.combine(end_date_for_dt, datetime.time(hour=end_hour, minute=end_minute))
    except ValueError as e:
        print(f"[DEBUG CRUD] Error during time string parsing or combination: {e}")
        pass 
    except Exception as e:
        print(f"[DEBUG CRUD] Unexpected error during time combination: {e}")
        pass 

    duration = calculate_duration_minutes(start_dt, end_dt)
    print(f"[DEBUG CRUD] Calculated Duration (minutes): {duration}")

    calculated_gained_exp = None
    if session.start_level is not None and \
       session.start_exp_percentage is not None and \
       session.end_level is not None and \
       session.end_exp_percentage is not None:
        print(f"[DEBUG CRUD] Inputs for gained_exp calc: start_level={session.start_level}, start_exp%={session.start_exp_percentage}, end_level={session.end_level}, end_exp%={session.end_exp_percentage}")
        calculated_gained_exp = calculate_gained_exp(
            start_level=session.start_level,
            start_exp_percentage=session.start_exp_percentage,
            end_level=session.end_level,
            end_exp_percentage=session.end_exp_percentage
        )
    else:
        print(f"[DEBUG CRUD] Skipped gained_exp calculation due to missing level/exp inputs.")
        
    print(f"[DEBUG CRUD] Calculated Gained EXP (gained_exp): {calculated_gained_exp}")

    calculated_base_experience_profit: Optional[float] = None
    coupon_count_from_session = session.coupon_15min_count if session.coupon_15min_count is not None else 0
    print(f"[DEBUG CRUD] Inputs for Base EXP Calc: gained_exp={calculated_gained_exp}, duration={duration}, coupon_count={coupon_count_from_session}")

    if calculated_gained_exp is not None and duration is not None and duration > 0:
        total_gained_exp_val = float(calculated_gained_exp)
        actual_coupon_minutes = min(coupon_count_from_session * 15, duration)
        non_coupon_minutes = duration - actual_coupon_minutes
        coupon_exp_rate = 2.0 
        effective_denominator_minutes = non_coupon_minutes + (actual_coupon_minutes * coupon_exp_rate)
        print(f"[DEBUG CRUD] Base EXP Calc Details: actual_coupon_minutes={actual_coupon_minutes}, non_coupon_minutes={non_coupon_minutes}, effective_denominator_minutes={effective_denominator_minutes}, coupon_exp_rate={coupon_exp_rate}")

        if effective_denominator_minutes > 0:
            base_exp_per_minute_no_coupon_effect = total_gained_exp_val / effective_denominator_minutes
            calculated_base_experience_profit = round(base_exp_per_minute_no_coupon_effect * duration)
            print(f"[DEBUG CRUD] Base EXP per minute (no coupon effect): {base_exp_per_minute_no_coupon_effect}, Calculated Base EXP (Branch 1): {calculated_base_experience_profit}")
        elif coupon_count_from_session > 0 and duration <= coupon_count_from_session * 15 and coupon_exp_rate > 0:
             calculated_base_experience_profit = round(total_gained_exp_val / coupon_exp_rate)
             print(f"[DEBUG CRUD] Base EXP (all coupon time - Branch 2): {calculated_base_experience_profit}")
        else: 
             calculated_base_experience_profit = float(total_gained_exp_val)
             print(f"[DEBUG CRUD] Base EXP (defaulted to gained_exp - Branch 3): {calculated_base_experience_profit}")
    elif calculated_gained_exp is not None:
        calculated_base_experience_profit = float(calculated_gained_exp)
        print(f"[DEBUG CRUD] Base EXP (no duration, gained_exp exists - Branch 4): {calculated_base_experience_profit}")
    else:
        calculated_base_experience_profit = 0.0
        print(f"[DEBUG CRUD] Base EXP (no gained_exp - Branch 5): {calculated_base_experience_profit}")
    
    print(f"[DEBUG CRUD] Final Calculated Base Experience Profit: {calculated_base_experience_profit}")

    db_session_data = {
        "session_date": session.session_date,
        "map_name": session.map_name,
        "start_time": session.start_time,
        "end_time": session.end_time,
        "duration_minutes": duration,
        "start_level": session.start_level,
        "start_exp_percentage": session.start_exp_percentage,
        "end_level": session.end_level,
        "end_exp_percentage": session.end_exp_percentage,
        "gained_exp": calculated_gained_exp,
        "base_experience_profit": calculated_base_experience_profit,
        "start_meso": session.start_meso,
        "end_meso": session.end_meso,
        "sold_meso": session.sold_meso,
        "coupon_15min_count": session.coupon_15min_count,
        "entry_fee": session.entry_fee,
        "hunting_meso_profit": session.hunting_meso_profit,
        "normal_item_profit": session.normal_item_profit,
        "total_rare_item_value": session.total_rare_item_value,
        "total_consumable_cost": session.total_consumable_cost,
        "total_consumable_gained_profit": session.total_consumable_gained_profit,
        "total_profit": session.total_profit,
        "net_profit": session.net_profit,
        "rare_items_detail": session.rare_items_detail,
        "consumable_items_detail": session.consumable_items_detail
    }
    
    print(f"[DEBUG CRUD] Data to be saved to DB: {db_session_data}")

    db_session = models.HuntingSessionLog(**db_session_data)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    print(f"[DEBUG CRUD] --- Finished create_hunting_session for map: {session.map_name} ---")
    return db_session


# =========================================
# Jjul Session CRUD
# =========================================
def get_jjul_session(db: Session, log_id: int):
    return db.query(models.JjulSessionLog).filter(models.JjulSessionLog.id == log_id).first()

def get_jjul_sessions(db: Session, skip: int = 0, limit: int = 100,
                      start_date: Optional[datetime.date] = None, 
                      end_date: Optional[datetime.date] = None,
                      map_name: Optional[str] = None):
    query = db.query(models.JjulSessionLog)
    if start_date:
        query = query.filter(models.JjulSessionLog.session_date >= start_date)
    if end_date:
        query = query.filter(models.JjulSessionLog.session_date <= end_date)
    if map_name:
        query = query.filter(models.JjulSessionLog.map_name == map_name)
        
    return query.order_by(
        models.JjulSessionLog.session_date.desc(), 
        models.JjulSessionLog.start_time.desc(),
        models.JjulSessionLog.id.desc()
    ).offset(skip).limit(limit).all()

def create_jjul_session(db: Session, session: schemas.JjulSessionCreate):
    start_dt: Union[datetime.datetime, None] = None
    end_dt: Union[datetime.datetime, None] = None
    duration: Union[int, None] = None

    try:
        if session.session_date and session.start_time:
            start_hour, start_minute = map(int, session.start_time.split(':'))
            start_dt = datetime.datetime.combine(session.session_date, datetime.time(hour=start_hour, minute=start_minute))
        
        if session.session_date and session.end_time:
            end_hour, end_minute = map(int, session.end_time.split(':'))
            end_date_for_dt = session.session_date 
            if start_dt and datetime.time(hour=end_hour, minute=end_minute) < start_dt.time():
                 end_date_for_dt += datetime.timedelta(days=1)
            end_dt = datetime.datetime.combine(end_date_for_dt, datetime.time(hour=end_hour, minute=end_minute))
        
        duration = calculate_duration_minutes(start_dt, end_dt)
    except ValueError as e:
        print(f"Warning: Jjul time string parsing or combination error - {e}")
        pass
    except Exception as e:
        print(f"Warning: Jjul unexpected error during time combination - {e}")
        pass

    db_session_data = {
        "session_date": session.session_date,
        "map_name": session.map_name,
        "start_time": session.start_time,
        "end_time": session.end_time,
        "duration_minutes": duration,
        "start_meso": session.start_meso,
        "end_meso": session.end_meso,
        "sold_meso": session.sold_meso,
        "party_size": session.party_size,
        "price_per_person": session.price_per_person,
        "total_jjul_fee": session.total_jjul_fee,
        "total_rare_item_value": session.total_rare_item_value,
        "total_consumable_cost": session.total_consumable_cost,
        "total_consumable_gained_profit": session.total_consumable_gained_profit,
        "normal_item_profit": session.normal_item_profit,
        "total_profit": session.total_profit,
        "net_profit": session.net_profit,
        "rare_items_detail": session.rare_items_detail,
        "consumable_items_detail": session.consumable_items_detail
    }

    db_session = models.JjulSessionLog(**db_session_data)
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
    return db.query(models.MesoSaleLog).order_by(
        models.MesoSaleLog.sale_date.desc(),
        models.MesoSaleLog.id.desc()
        ).offset(skip).limit(limit).all()

def create_meso_sale(db: Session, sale: schemas.MesoSaleCreate):
    db_sale = models.MesoSaleLog(
        sale_date=sale.sale_date,
        price_per_1m_meso=sale.price_per_1m_meso,
        quantity_sold_in_1m_units=sale.quantity_sold_in_1m_units,
        total_sale_amount_krw=sale.total_sale_amount_krw
    )
    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)
    return db_sale

# =========================================
# Statistics CRUD (수익 관련)
# =========================================
def get_daily_summary(db: Session, start_date: datetime.date, end_date: datetime.date) -> List[schemas.DailySummaryItem]:
    hunting_summary = db.query(
        models.HuntingSessionLog.session_date.label("date"),
        func.sum(models.HuntingSessionLog.hunting_meso_profit).label("total_hunting_meso"),
        func.sum(models.HuntingSessionLog.total_rare_item_value).label("total_rare_item_profit"),
        func.sum(models.HuntingSessionLog.normal_item_profit).label("total_normal_item_profit"),
        func.sum(models.HuntingSessionLog.total_consumable_gained_profit).label("total_consumable_gained"),
        func.sum(models.HuntingSessionLog.total_consumable_cost).label("total_consumable_cost"),
        func.sum(models.HuntingSessionLog.entry_fee).label("total_entry_fee"),
    ).filter(
        models.HuntingSessionLog.session_date >= start_date,
        models.HuntingSessionLog.session_date <= end_date
    ).group_by(models.HuntingSessionLog.session_date).all()

    jjul_summary = db.query(
        models.JjulSessionLog.session_date.label("date"),
        func.sum(models.JjulSessionLog.total_jjul_fee).label("total_jjul_profit"),
        func.sum(models.JjulSessionLog.total_rare_item_value).label("total_rare_item_profit"),
        func.sum(models.JjulSessionLog.normal_item_profit).label("total_normal_item_profit"),
        func.sum(models.JjulSessionLog.total_consumable_gained_profit).label("total_consumable_gained"),
        func.sum(models.JjulSessionLog.total_consumable_cost).label("total_consumable_cost"),
    ).filter(
        models.JjulSessionLog.session_date >= start_date,
        models.JjulSessionLog.session_date <= end_date
    ).group_by(models.JjulSessionLog.session_date).all()

    meso_sale_summary = db.query(
        models.MesoSaleLog.sale_date.label("date"),
        func.sum(models.MesoSaleLog.total_sale_amount_krw).label("total_cash_sold")
    ).filter(
        models.MesoSaleLog.sale_date >= start_date,
        models.MesoSaleLog.sale_date <= end_date
    ).group_by(models.MesoSaleLog.sale_date).all()

    summary_dict: Dict[datetime.date, Dict[str, int]] = {}
    
    current_date = start_date
    while current_date <= end_date:
        summary_dict[current_date] = {
            "hunting_meso": 0, "jjul_profit": 0, 
            "rare_item_profit": 0, "normal_item_profit": 0, 
            "consumable_gained_profit": 0, "consumable_cost": 0, 
            "entry_fee": 0, "cash_sold_krw": 0,
        }
        current_date += datetime.timedelta(days=1)

    for row in hunting_summary:
        date_key = row.date
        if date_key in summary_dict:
            summary_dict[date_key]["hunting_meso"] += row.total_hunting_meso or 0
            summary_dict[date_key]["rare_item_profit"] += row.total_rare_item_profit or 0
            summary_dict[date_key]["normal_item_profit"] += row.total_normal_item_profit or 0
            summary_dict[date_key]["consumable_gained_profit"] += row.total_consumable_gained or 0
            summary_dict[date_key]["consumable_cost"] += row.total_consumable_cost or 0
            summary_dict[date_key]["entry_fee"] += row.total_entry_fee or 0

    for row in jjul_summary:
        date_key = row.date
        if date_key in summary_dict:
            summary_dict[date_key]["jjul_profit"] += row.total_jjul_profit or 0
            summary_dict[date_key]["rare_item_profit"] += row.total_rare_item_profit or 0
            summary_dict[date_key]["normal_item_profit"] += row.total_normal_item_profit or 0
            summary_dict[date_key]["consumable_gained_profit"] += row.total_consumable_gained or 0
            summary_dict[date_key]["consumable_cost"] += row.total_consumable_cost or 0

    for row in meso_sale_summary:
        date_key = row.date
        if date_key in summary_dict:
            summary_dict[date_key]["cash_sold_krw"] += row.total_cash_sold or 0

    result_list: List[schemas.DailySummaryItem] = []
    for date_key, data in summary_dict.items():
        total_profit_calc = (data["hunting_meso"] + data["jjul_profit"] + 
                             data["rare_item_profit"] + data["normal_item_profit"] + 
                             data["consumable_gained_profit"])
        net_profit_calc = total_profit_calc - data["consumable_cost"] - data["entry_fee"]
        
        result_list.append(schemas.DailySummaryItem(
            date=date_key,
            hunting_meso=data["hunting_meso"],
            jjul_profit=data["jjul_profit"],
            rare_item_profit=data["rare_item_profit"],
            normal_item_profit=data["normal_item_profit"],
            consumable_gained_profit=data["consumable_gained_profit"],
            consumable_cost=data["consumable_cost"],
            entry_fee=data["entry_fee"],
            total_profit=total_profit_calc,
            net_profit=net_profit_calc,
            cash_sold_krw=data["cash_sold_krw"]
        ))
    result_list.sort(key=lambda x: x.date)
    return result_list


def get_map_summary(db: Session, start_date: Optional[datetime.date] = None, end_date: Optional[datetime.date] = None) -> List[schemas.MapSummaryItem]:
    hunting_query = db.query(
        models.HuntingSessionLog.map_name,
        func.count(models.HuntingSessionLog.id).label("hunt_count"),
        func.sum(models.HuntingSessionLog.total_profit).label("total_hunt_profit_from_model"),
        func.sum(models.HuntingSessionLog.total_rare_item_value).label("total_rare_profit"),
        func.sum(models.HuntingSessionLog.total_consumable_gained_profit).label("total_consumable_gained")
    )
    jjul_query = db.query(
        models.JjulSessionLog.map_name,
        func.count(models.JjulSessionLog.id).label("jjul_count"),
        func.sum(models.JjulSessionLog.total_profit).label("total_jjul_profit_from_model"),
        func.sum(models.JjulSessionLog.total_rare_item_value).label("total_rare_profit"),
        func.sum(models.JjulSessionLog.total_consumable_gained_profit).label("total_consumable_gained")
    )
    if start_date:
        hunting_query = hunting_query.filter(models.HuntingSessionLog.session_date >= start_date)
        jjul_query = jjul_query.filter(models.JjulSessionLog.session_date >= start_date)
    if end_date:
        hunting_query = hunting_query.filter(models.HuntingSessionLog.session_date <= end_date)
        jjul_query = jjul_query.filter(models.JjulSessionLog.session_date <= end_date)

    hunting_summary = hunting_query.group_by(models.HuntingSessionLog.map_name).all()
    jjul_summary = jjul_query.group_by(models.JjulSessionLog.map_name).all()

    map_dict: Dict[str, Dict[str, Union[int, float]]] = {}
    
    all_map_names = set()
    for row in hunting_summary: all_map_names.add(row.map_name)
    for row in jjul_summary: all_map_names.add(row.map_name)

    for map_name_key in all_map_names:
        if map_name_key is None: continue # 맵 이름이 없는 경우 스킵
        map_dict[map_name_key] = {
            "hunt_count": 0, "jjul_count": 0, 
            "total_hunt_profit": 0, "total_jjul_profit": 0, 
            "total_rare_item_profit": 0, "total_consumable_gained_profit": 0
        }

    for row in hunting_summary:
        map_name_key = row.map_name
        if map_name_key is None: continue
        map_dict[map_name_key]["hunt_count"] = row.hunt_count or 0
        map_dict[map_name_key]["total_hunt_profit"] = row.total_hunt_profit_from_model or 0
        map_dict[map_name_key]["total_rare_item_profit"] = (map_dict[map_name_key].get("total_rare_item_profit", 0) or 0) + (row.total_rare_profit or 0)
        map_dict[map_name_key]["total_consumable_gained_profit"] = (map_dict[map_name_key].get("total_consumable_gained_profit", 0) or 0) + (row.total_consumable_gained or 0)
        
    for row in jjul_summary:
        map_name_key = row.map_name
        if map_name_key is None: continue
        map_dict[map_name_key]["jjul_count"] = row.jjul_count or 0
        map_dict[map_name_key]["total_jjul_profit"] = row.total_jjul_profit_from_model or 0
        map_dict[map_name_key]["total_rare_item_profit"] = (map_dict[map_name_key].get("total_rare_item_profit", 0) or 0) + (row.total_rare_profit or 0)
        map_dict[map_name_key]["total_consumable_gained_profit"] = (map_dict[map_name_key].get("total_consumable_gained_profit", 0) or 0) + (row.total_consumable_gained or 0)

    result_list: List[schemas.MapSummaryItem] = []
    for map_name_key, data in map_dict.items():
        avg_hunt_profit = (data["total_hunt_profit"] / data["hunt_count"]) if data["hunt_count"] > 0 else 0
        avg_jjul_profit = (data["total_jjul_profit"] / data["jjul_count"]) if data["jjul_count"] > 0 else 0
        result_list.append(schemas.MapSummaryItem(
            map_name=map_name_key,
            hunt_count=int(data["hunt_count"]),
            jjul_count=int(data["jjul_count"]),
            total_hunt_profit=int(data["total_hunt_profit"]),
            total_jjul_profit=int(data["total_jjul_profit"]),
            total_rare_item_profit=int(data["total_rare_item_profit"]),
            total_consumable_gained_profit=int(data["total_consumable_gained_profit"]),
            average_hunt_profit=int(avg_hunt_profit),
            average_jjul_profit=int(avg_jjul_profit)
        ))
    result_list.sort(key=lambda x: (x.hunt_count + x.jjul_count), reverse=True)
    return result_list


def get_weekday_summary(db: Session, start_date: Optional[datetime.date] = None, end_date: Optional[datetime.date] = None) -> List[schemas.WeekdaySummaryItem]:
    python_weekday_order = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
    db_weekday_expression_hunt = cast(func.strftime('%w', models.HuntingSessionLog.session_date), SQLInteger)
    db_weekday_expression_jjul = cast(func.strftime('%w', models.JjulSessionLog.session_date), SQLInteger)

    hunting_query = db.query(
        db_weekday_expression_hunt.label("weekday_num_db"),
        func.sum(models.HuntingSessionLog.hunting_meso_profit).label("hunting_profit"),
        func.sum(models.HuntingSessionLog.total_rare_item_value).label("rare_profit"),
        func.sum(models.HuntingSessionLog.normal_item_profit).label("normal_profit"),
        func.sum(models.HuntingSessionLog.total_consumable_gained_profit).label("consumable_gained"),
        func.sum(models.HuntingSessionLog.net_profit).label("net_profit")
    )
    jjul_query = db.query(
        db_weekday_expression_jjul.label("weekday_num_db"),
        func.sum(models.JjulSessionLog.total_jjul_fee).label("jjul_profit"),
        func.sum(models.JjulSessionLog.total_rare_item_value).label("rare_profit"),
        func.sum(models.JjulSessionLog.normal_item_profit).label("normal_profit"),
        func.sum(models.JjulSessionLog.total_consumable_gained_profit).label("consumable_gained"),
        func.sum(models.JjulSessionLog.net_profit).label("net_profit")
    )

    if start_date:
        hunting_query = hunting_query.filter(models.HuntingSessionLog.session_date >= start_date)
        jjul_query = jjul_query.filter(models.JjulSessionLog.session_date >= start_date)
    if end_date:
        hunting_query = hunting_query.filter(models.HuntingSessionLog.session_date <= end_date)
        jjul_query = jjul_query.filter(models.JjulSessionLog.session_date <= end_date)

    hunting_summary = hunting_query.group_by("weekday_num_db").all()
    jjul_summary = jjul_query.group_by("weekday_num_db").all()

    py_weekday_map_to_name = {
        0: "월요일", 1: "화요일", 2: "수요일", 3: "목요일", 
        4: "금요일", 5: "토요일", 6: "일요일"
    }
    db_to_py_weekday_map = {0: 6, 1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5}

    weekday_dict: Dict[int, Dict[str, Union[str, int]]] = {}
    for py_weekday_num, name in py_weekday_map_to_name.items():
        weekday_dict[py_weekday_num] = {
            "weekday_name": name, "hunting_profit": 0, "jjul_profit": 0, 
            "rare_profit": 0, "normal_profit": 0, 
            "consumable_gained": 0, "total_profit": 0, "net_profit": 0
        }

    for row in hunting_summary:
        db_day_num = row.weekday_num_db
        if db_day_num is not None and db_day_num in db_to_py_weekday_map:
            py_day_num = db_to_py_weekday_map[db_day_num]
            weekday_dict[py_day_num]["hunting_profit"] = (weekday_dict[py_day_num].get("hunting_profit", 0) or 0) + (row.hunting_profit or 0)
            weekday_dict[py_day_num]["rare_profit"] = (weekday_dict[py_day_num].get("rare_profit", 0) or 0) + (row.rare_profit or 0)
            weekday_dict[py_day_num]["normal_profit"] = (weekday_dict[py_day_num].get("normal_profit", 0) or 0) + (row.normal_profit or 0)
            weekday_dict[py_day_num]["consumable_gained"] = (weekday_dict[py_day_num].get("consumable_gained", 0) or 0) + (row.consumable_gained or 0)
            weekday_dict[py_day_num]["net_profit"] = (weekday_dict[py_day_num].get("net_profit", 0) or 0) + (row.net_profit or 0)

    for row in jjul_summary:
        db_day_num = row.weekday_num_db
        if db_day_num is not None and db_day_num in db_to_py_weekday_map:
            py_day_num = db_to_py_weekday_map[db_day_num]
            weekday_dict[py_day_num]["jjul_profit"] = (weekday_dict[py_day_num].get("jjul_profit", 0) or 0) + (row.jjul_profit or 0)
            weekday_dict[py_day_num]["rare_profit"] = (weekday_dict[py_day_num].get("rare_profit", 0) or 0) + (row.rare_profit or 0)
            weekday_dict[py_day_num]["normal_profit"] = (weekday_dict[py_day_num].get("normal_profit", 0) or 0) + (row.normal_profit or 0)
            weekday_dict[py_day_num]["consumable_gained"] = (weekday_dict[py_day_num].get("consumable_gained", 0) or 0) + (row.consumable_gained or 0)
            weekday_dict[py_day_num]["net_profit"] = (weekday_dict[py_day_num].get("net_profit", 0) or 0) + (row.net_profit or 0)

    result_list: List[schemas.WeekdaySummaryItem] = []
    for py_weekday_num in sorted(weekday_dict.keys()): 
        data = weekday_dict[py_weekday_num]
        total_profit_calc = (data["hunting_profit"] + data["jjul_profit"] + 
                             data["rare_profit"] + data["normal_profit"] + 
                             data["consumable_gained"])
        
        result_list.append(schemas.WeekdaySummaryItem(
            weekday_name=str(data["weekday_name"]),
            hunting_profit=int(data["hunting_profit"]),
            jjul_profit=int(data["jjul_profit"]),
            rare_item_profit=int(data["rare_profit"]),
            normal_item_profit=int(data["normal_profit"]),
            consumable_gained_profit=int(data["consumable_gained"]),
            total_profit=total_profit_calc,
            net_profit=int(data["net_profit"])
        ))
    return result_list

# =========================================
# Unique Names CRUD
# =========================================
def get_unique_map_names(db: Session) -> List[str]:
    hunting_maps = db.query(models.HuntingSessionLog.map_name).distinct().all()
    jjul_maps = db.query(models.JjulSessionLog.map_name).distinct().all()
    unique_names = sorted(list(set([m[0] for m in hunting_maps if m[0]] + [m[0] for m in jjul_maps if m[0]])))
    return unique_names

def get_unique_rare_item_names(db: Session) -> List[str]:
    hunting_items = db.query(models.HuntingSessionLog.rare_items_detail).filter(models.HuntingSessionLog.rare_items_detail.isnot(None)).all()
    jjul_items = db.query(models.JjulSessionLog.rare_items_detail).filter(models.JjulSessionLog.rare_items_detail.isnot(None)).all()
    names = set()
    for item_detail_json_tuple in hunting_items + jjul_items:
        item_detail_json = item_detail_json_tuple[0]
        if not item_detail_json: continue
        try:
            items = json.loads(item_detail_json)
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict) and 'name' in item and item['name']:
                        names.add(item['name'])
        except (json.JSONDecodeError, TypeError): 
            print(f"Error decoding JSON or type error for rare_items_detail: {item_detail_json}")
            continue
    return sorted(list(names))

def get_unique_consumable_item_names(db: Session) -> List[str]:
    hunting_items = db.query(models.HuntingSessionLog.consumable_items_detail).filter(models.HuntingSessionLog.consumable_items_detail.isnot(None)).all()
    jjul_items = db.query(models.JjulSessionLog.consumable_items_detail).filter(models.JjulSessionLog.consumable_items_detail.isnot(None)).all()
    names = set()
    for item_detail_json_tuple in hunting_items + jjul_items:
        item_detail_json = item_detail_json_tuple[0]
        if not item_detail_json: continue
        try:
            items = json.loads(item_detail_json)
            if isinstance(items, list):
                for item in items:
                     if isinstance(item, dict) and 'name' in item and item['name']:
                        names.add(item['name'])
        except (json.JSONDecodeError, TypeError): 
            print(f"Error decoding JSON or type error for consumable_items_detail: {item_detail_json}")
            continue
    return sorted(list(names))

# =========================================
# ⭐ 경험치 통계 CRUD 함수들 ⭐
# =========================================
def get_daily_experience_summary(db: Session, start_date: datetime.date, end_date: datetime.date) -> List[schemas.DailyExperienceSummaryItem]:
    logs = db.query(
        models.HuntingSessionLog.session_date.label("date"),
        models.HuntingSessionLog.gained_exp,
        models.HuntingSessionLog.base_experience_profit,
        models.HuntingSessionLog.duration_minutes
    ).filter(
        models.HuntingSessionLog.session_date >= start_date,
        models.HuntingSessionLog.session_date <= end_date,
        models.HuntingSessionLog.gained_exp.isnot(None),
        models.HuntingSessionLog.duration_minutes.isnot(None),
        models.HuntingSessionLog.duration_minutes > 0
    ).order_by(models.HuntingSessionLog.session_date).all()

    daily_summaries: Dict[datetime.date, Dict[str, Union[int, float]]] = {}
    
    current_date = start_date
    while current_date <= end_date:
        daily_summaries[current_date] = {
            "total_session_count": 0, "total_duration_minutes": 0,
            "total_gained_exp": 0.0, "total_base_experience_profit": 0.0,
        }
        current_date += datetime.timedelta(days=1)

    for log in logs:
        log_date = log.date
        if log_date in daily_summaries:
            current_duration = log.duration_minutes or 0

            daily_summaries[log_date]["total_duration_minutes"] = (daily_summaries[log_date].get("total_duration_minutes",0) or 0) + current_duration
            daily_summaries[log_date]["total_session_count"] = (daily_summaries[log_date].get("total_session_count",0) or 0) + 1
            daily_summaries[log_date]["total_gained_exp"] = (daily_summaries[log_date].get("total_gained_exp",0.0) or 0.0) + (log.gained_exp or 0.0)
            daily_summaries[log_date]["total_base_experience_profit"] = (daily_summaries[log_date].get("total_base_experience_profit",0.0) or 0.0) + (log.base_experience_profit or 0.0)

    result_list: List[schemas.DailyExperienceSummaryItem] = []
    for date_key, summary in daily_summaries.items():
        total_duration_minutes = summary["total_duration_minutes"]
        total_gained_exp_val = summary["total_gained_exp"]
        total_base_exp_val = summary["total_base_experience_profit"]
        
        avg_exp_per_hour = 0.0
        avg_base_exp_per_hour = 0.0
        if total_duration_minutes > 0:
            total_duration_hours = total_duration_minutes / 60.0
            avg_exp_per_hour = round(total_gained_exp_val / total_duration_hours, 2) if total_gained_exp_val is not None else 0.0
            avg_base_exp_per_hour = round(total_base_exp_val / total_duration_hours, 2) if total_base_exp_val is not None else 0.0
            
        summary_item = schemas.DailyExperienceSummaryItem(
            date=date_key, 
            total_session_count=int(summary["total_session_count"]),
            total_duration_minutes=int(total_duration_minutes),
            total_experience_profit=float(total_gained_exp_val or 0.0),
            total_base_experience_profit=float(total_base_exp_val or 0.0),
            average_experience_per_hour=avg_exp_per_hour,
            average_base_experience_per_hour=avg_base_exp_per_hour,
        )
        result_list.append(summary_item)
    result_list.sort(key=lambda item: item.date)
    return result_list


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
            avg_exp_per_minute = float(results.total_exp) / float(results.total_minutes)
            return avg_exp_per_minute * 60
        except ZeroDivisionError: 
            return 0.0
    else: 
        return 0.0

def get_daily_exp_values(db: Session, start_date: Optional[datetime.date] = None, end_date: Optional[datetime.date] = None) -> Dict[datetime.date, schemas.DailyExpValues]:
    query = db.query(
        models.HuntingSessionLog.session_date.label("date"),
        func.sum(models.HuntingSessionLog.gained_exp).label("total_gained_exp"),
        func.sum(models.HuntingSessionLog.base_experience_profit).label("total_base_exp")
    ).filter(
        models.HuntingSessionLog.session_date.isnot(None),
        models.HuntingSessionLog.gained_exp.isnot(None)
    )
    if start_date:
        query = query.filter(models.HuntingSessionLog.session_date >= start_date)
    if end_date:
        query = query.filter(models.HuntingSessionLog.session_date <= end_date)

    query = query.group_by(models.HuntingSessionLog.session_date).order_by(models.HuntingSessionLog.session_date)
    results = query.all()
    
    daily_exp_dict: Dict[datetime.date, schemas.DailyExpValues] = {}
    for result in results:
        if result.date:
            daily_exp_dict[result.date] = schemas.DailyExpValues(
                gained_exp=int(result.total_gained_exp) if result.total_gained_exp is not None else 0,
                base_exp=float(result.total_base_exp) if result.total_base_exp is not None else None
            )
    return daily_exp_dict

def get_daily_total_gained_exp(db: Session, start_date: Optional[datetime.date] = None, end_date: Optional[datetime.date] = None) -> Dict[str, int]:
    query = db.query(
        models.HuntingSessionLog.session_date.label("date"),
        func.sum(models.HuntingSessionLog.gained_exp).label("daily_total_exp")
    ).filter(
        models.HuntingSessionLog.session_date.isnot(None),
        models.HuntingSessionLog.gained_exp.isnot(None),
        models.HuntingSessionLog.gained_exp > 0
    )
    if start_date:
        query = query.filter(models.HuntingSessionLog.session_date >= start_date)
    if end_date:
        query = query.filter(models.HuntingSessionLog.session_date <= end_date)

    query = query.group_by(models.HuntingSessionLog.session_date).order_by(models.HuntingSessionLog.session_date)
    results = query.all()
    
    daily_exp_dict = {
        result.date.isoformat(): (int(result.daily_total_exp) if result.daily_total_exp is not None else 0) 
        for result in results if result.date
    }
    return daily_exp_dict


# =========================================
# ⭐ 신규 CRUD 함수: 요일별 및 맵별 경험치 요약 (gained_exp 기반) ⭐
# =========================================
def get_experience_summary_by_weekday(
    db: Session, 
    start_date: Optional[datetime.date] = None, 
    end_date: Optional[datetime.date] = None
) -> List[schemas.ExperienceWeekdaySummaryItem]:
    py_weekday_order = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
    db_weekday_expression = cast(func.strftime('%w', models.HuntingSessionLog.session_date), SQLInteger)
    
    query = db.query(
        db_weekday_expression.label("weekday_num_db"),
        func.sum(models.HuntingSessionLog.gained_exp).label("total_gained_exp"),
        func.sum(models.HuntingSessionLog.duration_minutes).label("total_duration_minutes"),
        func.count(models.HuntingSessionLog.id).label("session_count")
    ).filter(
        models.HuntingSessionLog.gained_exp.isnot(None),
        models.HuntingSessionLog.gained_exp > 0,
        models.HuntingSessionLog.duration_minutes.isnot(None),
        models.HuntingSessionLog.duration_minutes > 0
    )

    if start_date:
        query = query.filter(models.HuntingSessionLog.session_date >= start_date)
    if end_date:
        query = query.filter(models.HuntingSessionLog.session_date <= end_date)

    query = query.group_by("weekday_num_db").order_by("weekday_num_db")
    results = query.all()

    weekday_summaries_dict: Dict[str, schemas.ExperienceWeekdaySummaryItem] = {
        name: schemas.ExperienceWeekdaySummaryItem(weekday_name=name) for name in py_weekday_order
    }
    
    db_to_py_weekday_name_map = {
        0: "일요일", 1: "월요일", 2: "화요일", 3: "수요일",
        4: "목요일", 5: "금요일", 6: "토요일"
    }

    for row in results:
        db_day_num = row.weekday_num_db
        if db_day_num is not None and db_day_num in db_to_py_weekday_name_map:
            py_weekday_name = db_to_py_weekday_name_map[db_day_num]
            
            summary = weekday_summaries_dict[py_weekday_name]
            summary.total_gained_exp += row.total_gained_exp or 0
            summary.total_duration_minutes += row.total_duration_minutes or 0
            summary.session_count += row.session_count or 0

    final_summary_list: List[schemas.ExperienceWeekdaySummaryItem] = []
    for weekday_name in py_weekday_order:
        summary = weekday_summaries_dict[weekday_name]
        if summary.total_duration_minutes > 0:
            summary.average_exp_per_hour = round(
                (summary.total_gained_exp / (summary.total_duration_minutes / 60.0)), 2
            )
        else:
            summary.average_exp_per_hour = 0.0
        final_summary_list.append(summary)
        
    return final_summary_list

# --- ✨ 신규 추가된 함수 ✨ ---
def get_experience_summary_by_map(
    db: Session, 
    start_date: Optional[datetime.date] = None, 
    end_date: Optional[datetime.date] = None
) -> List[schemas.ExperienceMapSummaryItem]:
    """
    지정된 기간 동안의 사냥 기록을 바탕으로 맵별 경험치 통계를 집계합니다.
    gained_exp가 있는 HuntingSessionLog 기록만 대상으로 합니다.
    결과는 총 획득 경험치가 높은 순으로 정렬됩니다.
    """
    
    query = db.query(
        models.HuntingSessionLog.map_name.label("map_name"),
        func.sum(models.HuntingSessionLog.gained_exp).label("total_gained_exp"),
        func.sum(models.HuntingSessionLog.duration_minutes).label("total_duration_minutes"),
        func.count(models.HuntingSessionLog.id).label("session_count")
    ).filter(
        models.HuntingSessionLog.map_name.isnot(None), # 맵 이름이 있는 경우만
        models.HuntingSessionLog.gained_exp.isnot(None),
        models.HuntingSessionLog.gained_exp > 0,
        models.HuntingSessionLog.duration_minutes.isnot(None),
        models.HuntingSessionLog.duration_minutes > 0
    )

    if start_date:
        query = query.filter(models.HuntingSessionLog.session_date >= start_date)
    if end_date:
        query = query.filter(models.HuntingSessionLog.session_date <= end_date)

    query = query.group_by(models.HuntingSessionLog.map_name).order_by(
        func.sum(models.HuntingSessionLog.gained_exp).desc() # 총 획득 경험치가 높은 순으로 정렬
    )

    results = query.all()

    summary_list: List[schemas.ExperienceMapSummaryItem] = []
    for row in results:
        map_name_val = row.map_name # 맵 이름이 None일 수 있으므로 안전하게 처리
        if map_name_val is None: # 맵 이름이 없는 데이터는 통계에서 제외 (또는 "알 수 없음" 등으로 처리)
            continue

        total_gained_exp = row.total_gained_exp or 0
        total_duration_minutes = row.total_duration_minutes or 0
        session_count = row.session_count or 0
        
        average_exp_per_hour = 0.0
        if total_duration_minutes > 0:
            average_exp_per_hour = round((total_gained_exp / (total_duration_minutes / 60.0)), 2)
        
        summary_item = schemas.ExperienceMapSummaryItem(
            map_name=map_name_val, # None이 아닌 맵 이름 사용
            total_gained_exp=total_gained_exp,
            total_duration_minutes=total_duration_minutes,
            session_count=session_count,
            average_exp_per_hour=average_exp_per_hour
        )
        summary_list.append(summary_item)
    
    return summary_list
# --- ✨ 신규 추가된 함수 끝 ✨ ---