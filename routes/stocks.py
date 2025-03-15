from fastapi import APIRouter, Request, Query
from dependencies import templates
from setup import db_dependency
from models import Stock
from sqlalchemy import select, func

router = APIRouter()

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
    
    return templates.TemplateResponse("stocks.html", {"request": request, 
                                                      "session_user_id": request.session["session_user_id"],
                                                      "stocks": stocks,
                                                      "page": page,
                                                      "total_pages": total_pages})