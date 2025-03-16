from setup import Base
from sqlalchemy import Column, Integer, String, Float, BigInteger, DateTime, ForeignKey, func, CheckConstraint
from sqlalchemy.orm import relationship


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
    
    
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    stock_id = Column(Integer, ForeignKey("stock.id"), nullable=False)

    order_type = Column(String(4), nullable=False)  # 'BUY' or 'SELL'
    order_quantity = Column(Integer, nullable=False)
    order_price = Column(Float, nullable=False)  # Market Price (from Stock model)
    
    status = Column(String(10), nullable=False, default="PENDING")  # 'PENDING' or 'CLOSED'
    order_created_at = Column(DateTime, default=func.now())
    matched_at = Column(DateTime, nullable=True)  # Timestamp when order is matched

    # Relationships
    user = relationship("User", backref="orders")
    stock = relationship("Stock", backref="orders")
    
    
class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    stock_id = Column(Integer, ForeignKey("stock.id"), nullable=False)

    inventory_quantity = Column(Integer, nullable=False, default=0)  # Number of stocks the user owns
    average_price = Column(Float, nullable=False, default=0.0)  # Average purchase price

    # Relationships
    user = relationship("User", backref="inventory")
    stock = relationship("Stock", backref="inventory")


class Transaction(Base):
    __tablename__ = "transaction"

    id = Column(Integer, primary_key=True, index=True)
    buy_order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)  # FK to Buy Order
    sell_order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)  # FK to Sell Order
    stock_id = Column(Integer, ForeignKey("stock.id"), nullable=False)  # FK to Stock

    transaction_quantity = Column(Integer, nullable=False)  # Matched trade quantity
    price_per_stock = Column(Float, nullable=False)  # Traded price per stock
    total_amount = Column(Float, nullable=False)  # Total trade value (quantity * price)

    executed_at = Column(DateTime, default=func.now())  # Timestamp when trade happened

    # Relationships
    buy_order = relationship("Order", foreign_keys=[buy_order_id], backref="buy_transaction")
    sell_order = relationship("Order", foreign_keys=[sell_order_id], backref="sell_transaction")
    stock = relationship("Stock", backref="transaction")
    