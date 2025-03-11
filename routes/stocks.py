from fastapi import APIRouter, Request
from dependencies import templates

router = APIRouter()

@router.get("/stocks")
async def stocks(request: Request):
    if "session_user_id" not in request.session:
        return templates.TemplateResponse("/error_pages/errors.html", {"request": request, "errors": [{"msg": "User not authenticated"}]})

    return templates.TemplateResponse("stocks.html", {"request": request, "session_user_id": request.session["session_user_id"]})



    
    
