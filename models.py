from setup import Base
from sqlalchemy import Column, Integer, String, Float, BigInteger, DateTime


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    balance = Column(Float, nullable=False, default=100000.0)


class Stock(Base):
    __tablename__ = "stock"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(255), unique=True, nullable=False)
    code_act = Column(String(50), unique=True, nullable=False)
    code = Column(String(50), unique=True, nullable=False)

    # Price Details
    ltp = Column(Float, nullable=False)
    price_open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    closeyest = Column(Float, nullable=False)

    # Change Details
    change = Column(Float, nullable=False)
    change_percent = Column(Float, nullable=False)

    # Volume Details
    volume = Column(BigInteger, nullable=False)
    volume_avg = Column(BigInteger, nullable=False)

    # Market Info
    marketcap = Column(BigInteger, nullable=False)
    pe_ratio = Column(Float, nullable=False)
    eps = Column(Float, nullable=False)
    outstanding_shares = Column(BigInteger, nullable=False)

    # 52-Week High & Low
    week_52_high = Column(Float, nullable=False)
    week_52_low = Column(Float, nullable=False)

    # Currency
    currency = Column(String(10), nullable=False, default="INR")

    # Trade Time
    traded_time = Column(DateTime, nullable=False)