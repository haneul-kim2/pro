# C:\pro\app\models.py (전체 수정본)

from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, BigInteger, Boolean, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func # server_default=func.now() 사용 위함

from .database import Base

# --- MesoSaleLog 테이블 모델 정의 ---
class MesoSaleLog(Base):
    __tablename__ = "meso_sales_log" # 테이블명 Git 기준

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sale_date = Column(Date, nullable=False, index=True) # Git 기준 필드명
    price_per_1m_meso = Column(Integer, nullable=False) # Git 기준 필드명
    quantity_sold_in_1m_units = Column(Float, nullable=False) # Git 기준 필드명
    total_sale_amount_krw = Column(Integer, nullable=False) # Git 기준 필드명
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return (f"<MesoSaleLog(id={self.id}, sale_date='{self.sale_date}', "
                f"price_per_1m_meso={self.price_per_1m_meso}, quantity_sold_in_1m_units={self.quantity_sold_in_1m_units}, "
                f"total_sale_amount_krw={self.total_sale_amount_krw})>")

# --- HuntingSessionLog 테이블 모델 정의 (사냥 세션 기록) ---
class HuntingSessionLog(Base):
    __tablename__ = "hunting_sessions_log" # 테이블명 Git 기준

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_date = Column(Date, nullable=False, index=True) # Git 기준 필드명
    map_name = Column(String, nullable=False, index=True)
    start_time = Column(String, nullable=True) # HH:MM 형식 문자열 저장
    end_time = Column(String, nullable=True)   # HH:MM 형식 문자열 저장
    duration_minutes = Column(Integer, nullable=True) # ✨ 계산된 사냥 시간(분) ✨

    start_level = Column(Integer, nullable=False) # ✨ 필수 입력으로 변경 고려 (스키마에서 이미 Field(...) 사용) ✨
    start_exp_percentage = Column(Float, nullable=False, default=0.0) # ✨ 추가된 필드 ✨
    end_level = Column(Integer, nullable=True)
    end_exp_percentage = Column(Float, nullable=True) # ✨ 추가된 필드 ✨
    gained_exp = Column(BigInteger, nullable=True) # ✨ 추가된 필드 ✨

    start_meso = Column(Integer, default=0)
    end_meso = Column(Integer, default=0)
    sold_meso = Column(Integer, default=0) # Git 기준 필드명
    coupon_15min_count = Column(Integer, default=0) # Git 기준 필드명 (coupon_used_count 에서 변경)
    start_experience = Column(Float, default=0) # Git 기준 Float 타입
    end_experience = Column(Float, default=0)   # Git 기준 Float 타입
    entry_fee = Column(Integer, default=0)
    hunting_meso_profit = Column(Integer, default=0)
    normal_item_profit = Column(Integer, default=0)
    total_rare_item_value = Column(Integer, default=0) # Git 기준 필드명 (rare_items_value 에서 변경)
    total_consumable_cost = Column(Integer, default=0) # Git 기준 필드명 (consumable_cost 에서 변경)
    total_consumable_gained_profit = Column(Integer, default=0) # Git 기준 필드명 (consumable_gain_value 에서 변경)
    total_profit = Column(Integer, default=0)
    net_profit = Column(Integer, default=0)
    experience_profit = Column(Float, default=0)   # Git 기준 Float 타입
    base_experience_profit = Column(Float, default=0) # Git 기준 Float 타입
    # character_name 필드는 현재 Git 모델에 없음. 필요시 추가.
    rare_items_detail = Column(String, nullable=True) # Git 스키마 기준 추가 (nullable=True 가정)
    consumable_items_detail = Column(String, nullable=True) # Git 스키마 기준 추가 (nullable=True 가정)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    rare_items = relationship("RareItemLog", back_populates="hunting_session", cascade="all, delete-orphan")
    consumable_items = relationship("ConsumableLog", back_populates="hunting_session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<HuntingSessionLog(id={self.id}, map_name='{self.map_name}', session_date='{self.session_date}')>"

# --- JjulSessionLog 테이블 모델 정의 (쩔 세션 기록) ---
class JjulSessionLog(Base):
    __tablename__ = "jjul_sessions_log" # 테이블명 Git 기준

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_date = Column(Date, nullable=False, index=True) # Git 기준 필드명
    map_name = Column(String, nullable=False, index=True)
    start_time = Column(String, nullable=True) # HH:MM 형식 문자열 저장
    end_time = Column(String, nullable=True)   # HH:MM 형식 문자열 저장
    duration_minutes = Column(Integer, nullable=True) # ✨ 계산된 쩔 시간(분) ✨

    start_meso = Column(Integer, default=0)
    end_meso = Column(Integer, default=0)
    sold_meso = Column(Integer, default=0) # Git 기준 필드명
    party_size = Column(Integer, default=0) # Git 기준 필드명 (party_members_count 에서 변경)
    price_per_person = Column(Integer, default=0) # Git 기준 필드명 (price_per_member 에서 변경)
    total_jjul_fee = Column(Integer, default=0)
    total_rare_item_value = Column(Integer, default=0) # Git 기준 필드명
    total_consumable_cost = Column(Integer, default=0) # Git 기준 필드명
    total_consumable_gained_profit = Column(Integer, default=0) # Git 기준 필드명
    normal_item_profit = Column(Integer, default=0)
    total_profit = Column(Integer, default=0)
    net_profit = Column(Integer, default=0)
    # character_name 필드는 현재 Git 모델에 없음. 필요시 추가.
    rare_items_detail = Column(String, nullable=True) # Git 스키마 기준 추가
    consumable_items_detail = Column(String, nullable=True) # Git 스키마 기준 추가

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    rare_items = relationship("RareItemLog", back_populates="jjul_session", cascade="all, delete-orphan")
    consumable_items = relationship("ConsumableLog", back_populates="jjul_session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<JjulSessionLog(id={self.id}, map_name='{self.map_name}', session_date='{self.session_date}')>"

# --- RareItemLog 테이블 모델 정의 ---
class RareItemLog(Base):
    __tablename__ = "rare_items_log" # 테이블명 Git 기준

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    item_name = Column(String, nullable=False)
    item_value = Column(Integer, default=0) # Git 기준 필드명
    hunting_session_id = Column(Integer, ForeignKey("hunting_sessions_log.id"), nullable=True, index=True)
    hunting_session = relationship("HuntingSessionLog", back_populates="rare_items")
    jjul_session_id = Column(Integer, ForeignKey("jjul_sessions_log.id"), nullable=True, index=True)
    jjul_session = relationship("JjulSessionLog", back_populates="rare_items")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<RareItemLog(id={self.id}, item_name='{self.item_name}', item_value={self.item_value})>"

# --- ConsumableLog 테이블 모델 정의 ---
class ConsumableLog(Base):
    __tablename__ = "consumable_items_log" # 테이블명 Git 기준

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    item_name = Column(String, nullable=False)
    price_or_value_per_item = Column(Integer, default=0) # Git 기준 필드명
    start_quantity = Column(Integer, default=0)
    end_quantity = Column(Integer, default=0)
    hunting_session_id = Column(Integer, ForeignKey("hunting_sessions_log.id"), nullable=True, index=True)
    hunting_session = relationship("HuntingSessionLog", back_populates="consumable_items")
    jjul_session_id = Column(Integer, ForeignKey("jjul_sessions_log.id"), nullable=True, index=True)
    jjul_session = relationship("JjulSessionLog", back_populates="consumable_items")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return (f"<ConsumableLog(id={self.id}, item_name='{self.item_name}', "
                f"start_qty={self.start_quantity}, end_qty={self.end_quantity})>")