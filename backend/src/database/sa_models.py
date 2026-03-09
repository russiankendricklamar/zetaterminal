"""
SQLAlchemy ORM models for Zeta Terminal.

Works with both Neon (PostgreSQL) and SQLite (desktop).
"""
from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class BondValuation(Base):
    __tablename__ = "bond_valuations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    secid = Column(String, nullable=False, index=True)
    valuation_date = Column(String, nullable=False)
    discount_yield1 = Column(Float, nullable=False)
    discount_yield2 = Column(Float, nullable=False)
    dirty_price = Column(Float, nullable=False)
    clean_price = Column(Float, nullable=False)
    ytm = Column(Float, nullable=False)
    duration = Column(Float, nullable=False)
    modified_duration = Column(Float, nullable=True)
    convexity = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    positions = Column(JSON, nullable=False)
    total_value = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CalculationHistory(Base):
    __tablename__ = "calculation_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    calculation_type = Column(String, nullable=False)
    input_data = Column(JSON, nullable=False)
    result_data = Column(JSON, nullable=False)
    execution_time_ms = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class MarketDataDaily(Base):
    __tablename__ = "market_data_daily"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String, nullable=False, index=True)
    data_type = Column(String, nullable=False)
    date = Column(String, nullable=False)
    price = Column(Float, nullable=True)
    volume = Column(Integer, nullable=True)
    change_percent = Column(Float, nullable=True)
    metadata_ = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("ticker", "data_type", "date", name="uq_market_data_ticker_type_date"),
    )


class ApiKey(Base):
    """Stores third-party API keys (replaces env vars)."""
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, autoincrement=True)
    service = Column(String, nullable=False, unique=True, index=True)
    key_value = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False, index=True)
    domain_handle = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    display_name = Column(String, nullable=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False, default="user")
    status = Column(String, nullable=False, default="pending")
    invite_code = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    activated_at = Column(DateTime, nullable=True)


class FileRecord(Base):
    __tablename__ = "file_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    metadata_ = Column("metadata", JSON, default=dict)
    created_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
