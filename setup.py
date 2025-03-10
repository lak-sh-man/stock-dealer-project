import os
from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from contextlib import asynccontextmanager
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState
import asyncio
from colorama import Back, Style

basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URL = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Import models before creating tables
import models  

# Creates db.sqlite file
Base.metadata.create_all(bind=engine)

########################################################################################

latest_stock_data = []

@asynccontextmanager
async def lifespan(app: FastAPI):
    global latest_stock_data  # Access the shared variable

    # Import inside the function to avoid circular imports
    from routes.stocks import fetch_stock_data
    from dependencies import get_db, db_dependency

    async def update_stock_data():
        global latest_stock_data
        while True:
            print("Fetching stock data...")
            latest_stock_data = await fetch_stock_data()  # Update the shared variable
            print(f"Fetched {len(latest_stock_data)} stocks")
            await asyncio.sleep(15)  # for each 15 sec, external api is called

    # Start the background tasks
    update_task = asyncio.create_task(update_stock_data())
    store_task = asyncio.create_task(store_stock_data(db_dependency))

    yield

    # Clean up when the app shuts down
    update_task.cancel()  # Cancel the update task
    store_task.cancel()  # Cancel the store task
    try:
        await update_task  # Wait for the task to be canceled
        await store_task
    except asyncio.CancelledError:
        pass  # Task was canceled, no action needed
    db_dependency.close()  # Close the database session

app = FastAPI(lifespan=lifespan)

########################################################################################

router = APIRouter()
connected_clients = {}

# WebSocket for real-time stock updates
@router.websocket("/ws/stocks/{user_id}")
async def stock_updates(websocket: WebSocket, user_id: str):
    global latest_stock_data  # Access the shared variable

    await websocket.accept()
    connected_clients[user_id] = websocket
    print(Back.GREEN + f"WebSocket connected => User ID: {user_id} | connected_clients: {list(connected_clients.keys())}" + Style.RESET_ALL)
    try:
        while True:
            print(len(latest_stock_data))
            if latest_stock_data:
                if websocket.client_state != WebSocketState.CONNECTED:
                    break  # Exit the loop if the connection is closed
                await websocket.send_json(latest_stock_data[0:100])  # Send the latest data
                print(Back.BLUE + f"Sent message to {user_id}" + Style.RESET_ALL)

            await asyncio.sleep(1)  # for each 10 sec, socket data is sent

    except WebSocketDisconnect:
        print(Back.MAGENTA + f"Exception so disconnecting => User ID: {user_id} | connected_clients: {connected_clients}" + Style.RESET_ALL)
    except Exception as e:
        print(Back.YELLOW + f"Unexpected error: {e} => User ID: {user_id}" + Style.RESET_ALL)
    finally:
        # Ensure the WebSocket is removed and closed properly
        if user_id in connected_clients:
            connected_clients.pop(user_id, None)
        if websocket.client_state == WebSocketState.CONNECTED:
            try:
                await websocket.close()
            except Exception as e:
                print(Back.RED + f"Error closing WebSocket: {e}" + Style.RESET_ALL)

        print(Back.RED + f"WebSocket disconnected => User ID: {user_id} | Remaining Clients: {list(connected_clients.keys())}" + Style.RESET_ALL)
        
########################################################################################

from dependencies import db_dependency
from models import Stock

# Background task to store stock data every minute
async def store_stock_data(db: db_dependency):
    print("Background task started: store_stock_data")
    global latest_stock_data  # Access the shared variable

    while True:
        if latest_stock_data:
            print(f"Processing {len(latest_stock_data)} stocks")
            stock_data = latest_stock_data[0:2]  # Take only the first 2 stocks for processing
            for stock in stock_data:
                print(f"Processing stock: {stock['Code']}")
                # Check if the stock already exists in the database using ORM syntax
                existing_stock = await db.get(Stock, stock["Code"])  # Use primary key (code) to fetch the stock
                if existing_stock:
                    print("Updating existing stock")
                    existing_stock.company_name = stock["Company_Name"]
                    existing_stock.code_act = stock["Code_act"]
                    existing_stock.ltp = stock["LTP"]
                    existing_stock.price_open = stock["Price_Open"]
                    existing_stock.high = stock["high"]
                    existing_stock.low = stock["low"]
                    existing_stock.closeyest = stock["closeyest"]
                    existing_stock.change = stock["change"]
                    existing_stock.change_percent = stock["Change_percent"]
                    existing_stock.volume = stock["Volume"]
                    existing_stock.volume_avg = stock["Volume_avg"]
                    existing_stock.marketcap = stock["Marketcap"]
                    existing_stock.pe_ratio = stock["PE"]
                    existing_stock.eps = stock["EPS"]
                    existing_stock.outstanding_shares = stock["Outstanding_Shares"]
                    existing_stock.week_52_high = stock["52_week_high"]
                    existing_stock.week_52_low = stock["52_week_low"]
                    existing_stock.currency = stock["currency"]
                    existing_stock.traded_time = stock["traded_time"]
                else:
                    print("Adding new stock")
                    db_stock = Stock(
                        company_name=stock["Company_Name"],
                        code_act=stock["Code_act"],
                        code=stock["Code"],
                        ltp=stock["LTP"],
                        price_open=stock["Price_Open"],
                        high=stock["high"],
                        low=stock["low"],
                        closeyest=stock["closeyest"],
                        change=stock["change"],
                        change_percent=stock["Change_percent"],
                        volume=stock["Volume"],
                        volume_avg=stock["Volume_avg"],
                        marketcap=stock["Marketcap"],
                        pe_ratio=stock["PE"],
                        eps=stock["EPS"],
                        outstanding_shares=stock["Outstanding_Shares"],
                        week_52_high=stock["52_week_high"],
                        week_52_low=stock["52_week_low"],
                        currency=stock["currency"],
                        traded_time=stock["traded_time"],
                    )
                    db.add(db_stock)

                await db.commit()  # Commit changes after processing each stock

        await asyncio.sleep(15)  # for each 15 sec, external api data is stored in db