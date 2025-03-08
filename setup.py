import os

from fastapi import FastAPI

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import asyncio
from contextlib import asynccontextmanager

basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URL = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Import models before creating tables
import models  

# Creates db.sqlite file
Base.metadata.create_all(bind=engine)


@asynccontextmanager 
async def lifespan(app: FastAPI):
    # imported inside the function to avoid circular imports
    from routes import stocks 
    from dependencies import db_dependency 
    
    task = asyncio.create_task(stocks.store_stock_data(db_dependency))  # Start storing stock data every minute
    yield  # Application is running
    task.cancel()  # Cleanup when shutting down 

app = FastAPI(lifespan=lifespan)

