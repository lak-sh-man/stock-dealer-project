from fastapi import APIRouter, Request
import httpx
import asyncio
from datetime import datetime
from dependencies import db_dependency, templates
from models import Stock
from external_api import STOCKS_API_URL

router = APIRouter()


@router.get("/stocks")
async def stocks(request: Request):
    if "session_user_id" not in request.session:
        return templates.TemplateResponse("/error_pages/errors.html", {"request": request, "errors": [{"msg": "User not authenticated"}]})

    return templates.TemplateResponse("stocks.html", {"request": request, "session_user_id": request.session["session_user_id"]})


# Fetch stock data from API
async def fetch_stock_data():
    async with httpx.AsyncClient(follow_redirects=True) as client:
        try:
            response = await client.get(STOCKS_API_URL)
            data = response.json()
            return data
        except Exception as e:
            return []
    
    
# Background task to store stock data every minute
async def store_stock_data(db: db_dependency):
    print("Background task started: store_stock_data")
    while True:
        print("Fetching stock data...")
        stock_data = await fetch_stock_data()
        print(f"Fetched {len(stock_data)} stocks")
        stock_data = stock_data[0:2]
        print(f"Taken {len(stock_data)} stocks")
        print(stock_data)
        for stock in stock_data:
            print(f"Processing stock: {stock['Code']}")
            # Check if the stock already exists in the database using ORM syntax
            existing_stock = await db.get(Stock, stock["Code"])  # Use primary key (code) to fetch the stock
            print(existing_stock)
            if existing_stock:
                print("existing")
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
                print("new")
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

        await asyncio.sleep(60)  # Wait for 60 seconds