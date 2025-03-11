import os
import httpx
from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.ext.declarative import declarative_base
from contextlib import asynccontextmanager
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState
import asyncio
from colorama import Back, Style
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.future import select



basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URL = 'sqlite+aiosqlite:///' + os.path.join(basedir, 'db.sqlite')
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False})
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

# Creates db.sqlite file
async def get_db():  
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()

########################################################################################

STOCKS_API_URL = "https://script.google.com/macros/s/AKfycbyE3x3exGpNQaIADJ8L8Vu6X9OyoHiU3uhGTgTKuKVsNT-X-C68JyiWsmkAj7ffqTT1/exec"

# Fetch stock data from API
async def fetch_stock_data():
    async with httpx.AsyncClient(follow_redirects=True) as client:
        try:
            response = await client.get(STOCKS_API_URL)
            response.raise_for_status()
            data = response.json()
            return data
        except httpx.HTTPStatusError as e:
            print(Back.YELLOW + f"⚠️ HTTP error: {e.response.status_code} - {e.response.text}" + Style.RESET_ALL)
        except httpx.RequestError as e:
            print(Back.YELLOW + f"⚠️ Network error: {e}" + Style.RESET_ALL)
        except Exception as e:
            print(Back.YELLOW + f"⚠️ Unexpected error: {e}" + Style.RESET_ALL)
        return []

########################################################################################

latest_stock_data = []

@asynccontextmanager
async def lifespan(app: FastAPI):
    global latest_stock_data  # Access the shared variable
    import models  # Import models before creating tables

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  # Ensure tables exist

    async def fetch_and_store():
        global latest_stock_data
        
        while True:
            print(Back.MAGENTA + "🔄 Fetching API data..." + Style.RESET_ALL)
            new_data = await fetch_stock_data()

            if new_data:
                latest_stock_data = new_data  # Update only if valid data is received
                print(Back.MAGENTA + f"✅ Fetched {len(latest_stock_data)} stocks" + Style.RESET_ALL)

            await asyncio.sleep(15)  # Wait 60 seconds before fetching again

    async def store_stock_data():
        """Store the in-memory latest fetched stock data in the database."""
        print(Back.MAGENTA + "💾 Storing stock data..." + Style.RESET_ALL)
        global latest_stock_data  
        from models import Stock

        async with SessionLocal() as db:
            while True:
                if latest_stock_data:
                    stock_data_copy = latest_stock_data.copy()  # Prevent modification during processing
                    print(Back.MAGENTA + f"📦 Processing {len(stock_data_copy)} stocks" + Style.RESET_ALL)
                    stock_data = stock_data_copy[:2]  # Process only the first 2 stocks

                    for stock in stock_data:
                        print(Back.MAGENTA + f"📦 Processing stock: {stock}" + Style.RESET_ALL)
                        stmt = select(Stock).where(Stock.code == stock["Code"])
                        result = await db.execute(stmt)
                        existing_stock = result.scalars().first()

                        if existing_stock:
                            print(Back.MAGENTA + "🅰️ Updating existing stock" + Style.RESET_ALL + Style.RESET_ALL)
                            existing_stock.company_name = str(stock["Company_Name"])
                            existing_stock.ltp = str(stock["LTP"])
                            existing_stock.price_open = str(stock["Price_Open"])
                            existing_stock.high = str(stock["high"])
                            existing_stock.low = str(stock["low"])
                            existing_stock.closeyest = str(stock["closeyest"])
                            existing_stock.change = str(stock["change"])
                            existing_stock.change_percent = str(stock["Change_percent"])
                            existing_stock.volume = str(stock["Volume"])
                            existing_stock.volume_avg = str(stock["Volume_avg"])
                            existing_stock.marketcap = str(stock["Marketcap"])
                            existing_stock.pe_ratio = str(stock["PE"])
                            existing_stock.eps = str(stock["EPS"])
                            existing_stock.outstanding_shares = str(stock["Outstanding_Shares"])
                            existing_stock.week_52_high = str(stock["52_week_high"])
                            existing_stock.week_52_low = str(stock["52_week_low"])
                            existing_stock.currency = str(stock["currency"])
                            existing_stock.traded_time = str(stock["traded_time"])
                        else:
                            print(Back.MAGENTA + "🅱️ Adding new stock" + Style.RESET_ALL + Style.RESET_ALL)
                            db_stock = Stock(
                                company_name=str(stock["Company_Name"]),
                                code=str(stock["Code"]),
                                ltp=str(stock["LTP"]),
                                price_open=str(stock["Price_Open"]),
                                high=str(stock["high"]),
                                low=str(stock["low"]),
                                closeyest=str(stock["closeyest"]),
                                change=str(stock["change"]),
                                change_percent=str(stock["Change_percent"]),
                                volume=str(stock["Volume"]),
                                volume_avg=str(stock["Volume_avg"]),
                                marketcap=str(stock["Marketcap"]),
                                pe_ratio=str(stock["PE"]),
                                eps=str(stock["EPS"]),
                                outstanding_shares=str(stock["Outstanding_Shares"]),
                                week_52_high=str(stock["52_week_high"]),
                                week_52_low=str(stock["52_week_low"]),
                                currency=str(stock["currency"]),
                                traded_time=str(stock["traded_time"]),
                            )
                            print(Back.MAGENTA + "before adding" + Style.RESET_ALL + Style.RESET_ALL)
                            db.add(db_stock)
                            print(Back.MAGENTA + "after adding" + Style.RESET_ALL + Style.RESET_ALL)

                    await db.commit()
                    print(Back.MAGENTA + "✅ Database update successful!" + Style.RESET_ALL)
                await asyncio.sleep(15)

    update_task = asyncio.create_task(fetch_and_store())
    store_task = asyncio.create_task(store_stock_data())

    yield  # Keep the lifespan active

    update_task.cancel()
    store_task.cancel()
    try:
        await update_task
        await store_task
    except asyncio.CancelledError:
        pass

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
            print(Back.WHITE + f"{len(latest_stock_data)}" + Style.RESET_ALL)
            if latest_stock_data:
                if websocket.client_state != WebSocketState.CONNECTED:
                    break  # Exit the loop if the connection is closed
                await websocket.send_json(latest_stock_data[0:100])  # Send the latest data
                print(Back.BLUE + f"Sent message to {user_id}" + Style.RESET_ALL)

            await asyncio.sleep(1)  # for each 10 sec, socket data is sent

    except WebSocketDisconnect:
        print(Back.YELLOW + f"Exception so disconnecting => User ID: {user_id} | connected_clients: {connected_clients}" + Style.RESET_ALL)
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
        
