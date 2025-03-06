from setup import Base
from sqlalchemy import Column, Integer, String, Float


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    balance = Column(Float, nullable=False, default=100000.0)
