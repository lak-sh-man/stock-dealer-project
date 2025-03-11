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
            print(f"⚠️ HTTP error: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            print(f"⚠️ Network error: {e}")
        except Exception as e:
            print(f"⚠️ Unexpected error: {e}")
        return []

########################################################################################

latest_stock_data = []
data_available_event = asyncio.Event()  # Event to signal when data is available

@asynccontextmanager
async def lifespan(app: FastAPI):
    global latest_stock_data, data_available_event  # Access the shared variable
    import models  # Import models before creating tables

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  # Ensure tables exist

    async def update_stock_data():
        global latest_stock_data, data_available_event
        
        while True:
            print(Back.WHITE + "Fetching api data..." + Style.RESET_ALL)
            latest_stock_data = await fetch_stock_data()  # Update the shared variable
            if latest_stock_data:  # Only update if new data is available
                print(Back.YELLOW + f"stock data response is successful" + Style.RESET_ALL)
                data_available_event.set() 
            print(Back.WHITE + f"Fetched {len(latest_stock_data)} stocks" + Style.RESET_ALL)
            await asyncio.sleep(60)  # for each 60 sec, external api is called

    async def store_stock_data():
        print(Back.YELLOW + f"entered inside store_stock_data" + Style.RESET_ALL)
        global latest_stock_data, data_available_event
        from models import Stock

        print(Back.YELLOW + f"waiting outside SessionLocal()" + Style.RESET_ALL)
        async with SessionLocal() as db:
            print(Back.YELLOW + f"entered inside SessionLocal()" + Style.RESET_ALL)
            while True:
                # now storing in the database starts only after new stock data is fetched, just like in synchronous execution.
                print(Back.YELLOW + f"waiting for green signal" + Style.RESET_ALL)
                await data_available_event.wait()  # Wait until new data is available
                data_available_event.clear()  # Reset the event after processing
                print(Back.YELLOW + f"green signal sent" + Style.RESET_ALL)
                
                if latest_stock_data:
                    stock_data_copy = latest_stock_data.copy()  # Prevent overwrite
                    print(Back.WHITE + f"Processing {len(latest_stock_data)} stocks" + Style.RESET_ALL)
                    stock_data = stock_data_copy[:2]  # Take only the first 2 stocks

                    for stock in stock_data:
                        print(Back.WHITE + f"Processing stock: {stock}" + Style.RESET_ALL)
                        stmt = select(Stock).where(Stock.code == stock["Code"])
                        result = await db.execute(stmt)
                        existing_stock = result.scalars().first()

                        if existing_stock:
                            print(Back.WHITE + "Updating existing stock" + Style.RESET_ALL)
                            existing_stock.company_name = stock["Company_Name"]
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
                            print(Back.WHITE + "Adding new stock" + Style.RESET_ALL)
                            db_stock = Stock(
                                company_name=stock["Company_Name"],
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

                    await db.commit()  # Save changes to DB
                    print(Back.WHITE + "✅ Database commit successful!" + Style.RESET_ALL)
                

    update_task = asyncio.create_task(update_stock_data())
    store_task = asyncio.create_task(store_stock_data())

    yield # this is literally an await for the lifespan function to run the scheduled update_task & store_task

    # Clean up when the app shuts down
    update_task.cancel()  # Cancel the update task
    store_task.cancel()  # Cancel the store task
    try:
        await update_task  # Wait for the task to be canceled
        await store_task
    except asyncio.CancelledError:
        pass  # Task was canceled, no action needed

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
        
