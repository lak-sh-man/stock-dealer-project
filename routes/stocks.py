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
    async with httpx.AsyncClient() as client:
        response = await client.get(STOCKS_API_URL)
        if response.status_code == 200:
            return response.json()
        return []
    
    
# Background task to store stock data every minute
async def store_stock_data(
    db: db_dependency
):
    while True:
        stock_data = await fetch_stock_data()
        for stock in stock_data:
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
                    traded_time=datetime.strptime(stock["traded_time"], "%Y-%m-%dT%H:%M:%S.%fZ"),
                )
            db.add(db_stock)
        db.commit()
        db.close()
        await asyncio.sleep(60)  # Store data every 1 minute
        