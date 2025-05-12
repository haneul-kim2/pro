# C:\pro\app\models.py

from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func # 기본값으로 현재 시간을 사용하기 위해

# app 폴더 내의 database.py에서 정의한 Base 클래스를 가져옵니다.
from .database import Base

# --- MesoSaleLog 테이블 모델 정의 ---
class MesoSaleLog(Base):
    __tablename__ = "meso_sales_log"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sale_date = Column(Date, nullable=False, index=True)
    price_per_1m_meso = Column(Integer, nullable=False)
    quantity_sold_in_1m_units = Column(Float, nullable=False)
    total_sale_amount_krw = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return (f"<MesoSaleLog(id={self.id}, sale_date='{self.sale_date}', "
                f"price_per_1m_meso={self.price_per_1m_meso}, quantity_sold_in_1m_units={self.quantity_sold_in_1m_units}, "
                f"total_sale_amount_krw={self.total_sale_amount_krw})>")

# --- HuntingSessionLog 테이블 모델 정의 (사냥 세션 기록) ---
class HuntingSessionLog(Base):
    __tablename__ = "hunting_sessions_log"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_date = Column(Date, nullable=False, index=True)
    map_name = Column(String, nullable=False, index=True)
    start_time = Column(String, nullable=True)
    end_time = Column(String, nullable=True)
    start_meso = Column(Integer, default=0)
    end_meso = Column(Integer, default=0)
    sold_meso = Column(Integer, default=0)
    coupon_15min_count = Column(Integer, default=0)
    start_experience = Column(Float, default=0)
    end_experience = Column(Float, default=0)
    entry_fee = Column(Integer, default=0)
    hunting_meso_profit = Column(Integer, default=0)
    normal_item_profit = Column(Integer, default=0)
    total_rare_item_value = Column(Integer, default=0)
    total_consumable_cost = Column(Integer, default=0)
    total_consumable_gained_profit = Column(Integer, default=0)
    total_profit = Column(Integer, default=0)
    net_profit = Column(Integer, default=0)
    experience_profit = Column(Float, default=0)
    base_experience_profit = Column(Float, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # 관계 설정은 아래 RareItemLog, ConsumableLog, JjulSessionLog가 모두 정의된 후에 오는 것이 좋습니다.
    # 여기서는 각 모델 정의 시 back_populates를 사용하므로 순서는 크게 중요하지 않으나,
    # 가독성을 위해 JjulSessionLog 정의 후 관계를 명시하는 것도 좋습니다.
    # 지금은 각 모델 내에서 관계를 정의하는 방식을 따릅니다.
    rare_items = relationship("RareItemLog", back_populates="hunting_session", cascade="all, delete-orphan")
    consumable_items = relationship("ConsumableLog", back_populates="hunting_session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<HuntingSessionLog(id={self.id}, map_name='{self.map_name}', session_date='{self.session_date}')>"


# --- JjulSessionLog 테이블 모델 정의 (쩔 세션 기록) ---
# RareItemLog와 ConsumableLog가 이 모델을 참조하므로, 먼저 정의합니다.
class JjulSessionLog(Base):
    __tablename__ = "jjul_sessions_log"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_date = Column(Date, nullable=False, index=True)
    map_name = Column(String, nullable=False, index=True)
    start_time = Column(String, nullable=True)
    end_time = Column(String, nullable=True)
    start_meso = Column(Integer, default=0)
    end_meso = Column(Integer, default=0)
    sold_meso = Column(Integer, default=0)
    party_size = Column(Integer, default=0)
    price_per_person = Column(Integer, default=0)
    total_jjul_fee = Column(Integer, default=0)
    total_rare_item_value = Column(Integer, default=0)
    total_consumable_cost = Column(Integer, default=0)
    total_consumable_gained_profit = Column(Integer, default=0)
    normal_item_profit = Column(Integer, default=0)
    total_profit = Column(Integer, default=0)
    net_profit = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    rare_items = relationship("RareItemLog", back_populates="jjul_session", cascade="all, delete-orphan")
    consumable_items = relationship("ConsumableLog", back_populates="jjul_session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<JjulSessionLog(id={self.id}, map_name='{self.map_name}', session_date='{self.session_date}')>"


# --- RareItemLog 테이블 모델 정의 (수정: JjulSessionLog 관계 추가) ---
class RareItemLog(Base):
    __tablename__ = "rare_items_log"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    item_name = Column(String, nullable=False)
    item_value = Column(Integer, default=0)

    # HuntingSessionLog와의 관계
    hunting_session_id = Column(Integer, ForeignKey("hunting_sessions_log.id"), nullable=True, index=True)
    hunting_session = relationship("HuntingSessionLog", back_populates="rare_items")

    # JjulSessionLog와의 관계 (새로 추가)
    jjul_session_id = Column(Integer, ForeignKey("jjul_sessions_log.id"), nullable=True, index=True)
    jjul_session = relationship("JjulSessionLog", back_populates="rare_items") # JjulSessionLog.rare_items와 연결

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<RareItemLog(id={self.id}, item_name='{self.item_name}', item_value={self.item_value})>"


# --- ConsumableLog 테이블 모델 정의 (수정: JjulSessionLog 관계 추가) ---
class ConsumableLog(Base):
    __tablename__ = "consumable_items_log"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    item_name = Column(String, nullable=False)
    price_or_value_per_item = Column(Integer, default=0)
    start_quantity = Column(Integer, default=0)
    end_quantity = Column(Integer, default=0)

    # HuntingSessionLog와의 관계
    hunting_session_id = Column(Integer, ForeignKey("hunting_sessions_log.id"), nullable=True, index=True)
    hunting_session = relationship("HuntingSessionLog", back_populates="consumable_items")

    # JjulSessionLog와의 관계 (새로 추가)
    jjul_session_id = Column(Integer, ForeignKey("jjul_sessions_log.id"), nullable=True, index=True)
    jjul_session = relationship("JjulSessionLog", back_populates="consumable_items") # JjulSessionLog.consumable_items와 연결

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return (f"<ConsumableLog(id={self.id}, item_name='{self.item_name}', "
                f"start_qty={self.start_quantity}, end_qty={self.end_quantity})>")