from fastapi import APIRouter, Request, Form
from dependencies import templates
from setup import db_dependency
from pydantic import ValidationError
from fastapi.responses import RedirectResponse
from models import User
from pydantic import BaseModel, Field
from sqlalchemy import select

router = APIRouter()

class Login_pyd_schema(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=3, max_length=255)

@router.get("/login")
async def login_get(request: Request):
    if "session_user_id" in request.session:
        return templates.TemplateResponse("/error_pages/errors.html", {"request": request, "errors": [{"msg": "logout to access the login page"}]})
    
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def login_post(
    request: Request,
    db: db_dependency,
    username: str = Form(...),
    password: str = Form(...)
):
    # Validate using Pydantic Model
    try:
        login_data = Login_pyd_schema(username=username, password=password)
    except ValidationError as e:
        return templates.TemplateResponse("login.html", {"request": request, "errors": e.errors()})

    # Check user in database
    results = await db.execute(select(User).where(User.username == login_data.username))
    user = results.scalars().first()  # Extract the first result
    # query syntax is not supported in asunc db
    # user = db.query(User).filter(User.username == login_data.username).first()
    if user and user.password == login_data.password:
        request.session["session_user_id"] = user.id
        request.session["session_user_name"] = user.username
        
        return RedirectResponse(url="/", status_code=302)

    return templates.TemplateResponse("login.html", {"request": request, "errors": [{"msg": "Invalid username or password"}]})

