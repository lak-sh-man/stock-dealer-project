from fastapi import APIRouter, Request
from dependencies import templates
from fastapi.responses import RedirectResponse

router = APIRouter()




@router.get("/logout")
async def logout(request: Request):
    if "session_user_id" not in request.session:
        return templates.TemplateResponse("/error_pages/errors.html", {"request": request, "errors": [{"msg": "User not authenticated"}]})

    # Clear session and redirect to login page
    request.session.clear()
    return RedirectResponse(url="/login", status_code=302)