from fastapi import APIRouter, Request
from dependencies import db_dependency, templates
from fastapi.responses import RedirectResponse

router = APIRouter()




@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=302)