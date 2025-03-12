from setup import Base
from sqlalchemy import Column, Integer, String, Float, BigInteger, DateTime


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    virtual_balance = Column(Float, nullable=False, default=100000.0)


class Stock(Base):
    __tablename__ = "stock"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(255), unique=True, nullable=False)
    code_act = Column(String(50), unique=True, nullable=False)
    code = Column(String(50), unique=True, nullable=False)

    # Price Details
    ltp = Column(String(50), nullable=False)
    price_open = Column(String(50), nullable=False)
    high = Column(String(50), nullable=False)
    low = Column(String(50), nullable=False)
    closeyest = Column(String(50), nullable=False)

    # Change Details
    change = Column(String(50), nullable=False)
    change_percent = Column(String(50), nullable=False)

    # Volume Details
    volume = Column(String(50), nullable=False)
    volume_avg = Column(String(50), nullable=False)

    # Market Info
    marketcap = Column(String(50), nullable=False)
    pe_ratio = Column(String(50), nullable=False)
    eps = Column(String(50), nullable=False)
    outstanding_shares = Column(String(50), nullable=False)

    # 52-Week High & Low
    week_52_high = Column(String(50), nullable=False)
    week_52_low = Column(String(50), nullable=False)

    # Currency
    currency = Column(String(10), nullable=False, default="INR")

    # Trade Time
    traded_time = Column(String(50), nullable=False)
    
    # virtual stocks
    virtual_stocks = Column(Integer, nullable=False, default=100000)