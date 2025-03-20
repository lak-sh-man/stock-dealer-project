from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/account")
async def account(request: Request):
    return templates.TemplateResponse("account.html", {"request": request})
