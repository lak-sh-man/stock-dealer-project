from fastapi import APIRouter, Request, Form
from dependencies import db_dependency, templates
from schema import Register_pyd_schema
from pydantic import ValidationError
from fastapi.responses import RedirectResponse
from models import User

router = APIRouter()



@router.get("/register")
async def register_get(request: Request):
    if "session_user_id" in request.session:
        return templates.TemplateResponse("/error_pages/errors.html", {"request": request, "errors": [{"msg": "logout to access the register page"}]})
    
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register")
async def register_post(
    request: Request,
    db: db_dependency,
    username: str = Form(...),
    password: str = Form(...),
    pass_confirm: str = Form(...)
):
    # Validate using Pydantic Model
    try:
        register_data = Register_pyd_schema(username=username, password=password, pass_confirm=pass_confirm)
        if register_data.password != register_data.pass_confirm:
            raise ValidationError([{"loc": ("password",), "msg": "Passwords do not match"}])
    except ValidationError as e:
        return templates.TemplateResponse("register.html", {"request": request, "errors": e.errors()})

    # Save user to database
    user = User(username=register_data.username, password=register_data.password)
    db.add(user)
    db.commit()

    return RedirectResponse(url="/login", status_code=302)