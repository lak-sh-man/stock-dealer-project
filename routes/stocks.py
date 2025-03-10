from fastapi import APIRouter, Request
import httpx
from dependencies import templates
from models import Stock

router = APIRouter()

STOCKS_API_URL = "https://script.google.com/macros/s/AKfycbyE3x3exGpNQaIADJ8L8Vu6X9OyoHiU3uhGTgTKuKVsNT-X-C68JyiWsmkAj7ffqTT1/exec"

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
    
    
