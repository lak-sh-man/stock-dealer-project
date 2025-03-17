from fastapi import APIRouter, Request, Query, Form
from dependencies import templates
from setup import db_dependency
from models import Stock
from sqlalchemy import select, func
from pydantic import BaseModel, Field, ValidationError

router = APIRouter()

class Stocks_pyd_schema(BaseModel):
    order_quantity: int = Field(..., gt=0, le=100000)


@router.get("/stocks")
async def stocks(request: Request, 
                 db: db_dependency,
                 page: int = 1,
                 per_page: int = 30
                ):
    if "session_user_id" not in request.session:
        return templates.TemplateResponse("/error_pages/errors.html", {"request": request, "errors": [{"msg": "User not authenticated"}]})

    # Calculate the offset for pagination
    offset = (page - 1) * per_page

    # Get total stocks count
    total_count = await db.execute(select(func.count()).select_from(Stock))
    total_pages = (total_count.scalar() // per_page) + 1

    # Fetch paginated stocks
    results = await db.execute(select(Stock).offset(offset).limit(per_page))
    stocks = results.scalars().all()
    
    # Extract stock symbols (or IDs) to send via WebSocket
    stock_codes = [stock.code for stock in stocks]  # Use stock_id if preferred
    return templates.TemplateResponse("stocks.html", {"request": request, 
                                                      "session_user_id": request.session["session_user_id"],
                                                      "stocks": stocks,
                                                      "page": page,
                                                      "total_pages": total_pages,
                                                      "stock_codes": stock_codes})
    

@router.get("/place_order")
async def place_order_get(request: Request,
                          stock_code: str,
                         ):
    if "session_user_id" not in request.session:
        return templates.TemplateResponse("/error_pages/errors.html", {"request": request, "errors": [{"msg": "User not authenticated"}]})
    return templates.TemplateResponse("place_order.html", {"request": request,
                                                           "stock_code": stock_code})
    

@router.post("/place_order")
async def place_order_post(request: Request,
                           order_quantity = Form(...)
                          ):
    # Validate using Pydantic Model
    try:
        login_data = Stocks_pyd_schema(order_quantity=order_quantity)
    except ValidationError as e:
        return templates.TemplateResponse("place_order.html", {"request": request, "errors": e.errors()})