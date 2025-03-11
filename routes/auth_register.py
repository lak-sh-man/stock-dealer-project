from fastapi import APIRouter, Request, Form
from dependencies import db_dependency, templates
from pydantic import ValidationError
from fastapi.responses import RedirectResponse
from models import User
from pydantic import BaseModel, Field
from sqlalchemy import select

router = APIRouter()

class Register_pyd_schema(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=3, max_length=255)
    pass_confirm: str = Field(..., min_length=3, max_length=255)


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
            return templates.TemplateResponse("register.html", {"request": request, "errors": [{"msg": "Passwords do not match"}]})
    except ValidationError as e:
        return templates.TemplateResponse("register.html", {"request": request, "errors": e.errors()})

    results = await db.execute(select(User).where(User.username == register_data.username))
    existing_user = results.scalars().first()  # Extract the first result
    # query syntax is not supported in asunc db
    # existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        return templates.TemplateResponse("register.html", {"request": request, "errors": [{"msg": "username already exist"}]})
    

    # Save user to database
    user = User(username=register_data.username, password=register_data.password)
    db.add(user)
    await db.commit()

    return RedirectResponse(url="/login", status_code=302)