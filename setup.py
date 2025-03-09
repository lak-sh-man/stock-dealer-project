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
    # Import inside the function to avoid circular imports
    from routes.stocks import store_stock_data
    from dependencies import get_db

    # Create a database session
    db = next(get_db())

    # Start the background task
    task = asyncio.create_task(store_stock_data(db))

    yield

    # Clean up when the app shuts down
    task.cancel()  # Cancel the background task
    try:
        await task  # Wait for the task to be canceled
    except asyncio.CancelledError:
        pass  # Task was canceled, no action needed
    db.close()  # Close the database session

app = FastAPI(lifespan=lifespan)

