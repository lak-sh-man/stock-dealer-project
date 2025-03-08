import uvicorn
from setup import app, SessionLocal
from models import User
from schema import Register_pyd_schema, Login_pyd_schema
from pydantic import ValidationError
from typing import Annotated

from fastapi import Depends, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

# Add session support (like Flask sessions)
app.add_middleware(SessionMiddleware, secret_key="your_secret_key")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Annotated Dependency for DB Session
db_dependency = Annotated[Session, Depends(get_db)]

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/register")
async def register_get(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register")
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

    return RedirectResponse(url="/login", status_code=303)


@app.get("/login")
async def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
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
    user = db.query(User).filter(User.username == login_data.username).first()
    if user and user.password == login_data.password:
        request.session["session_user_id"] = user.id
        request.session["session_user_name"] = user.username
        return RedirectResponse(url="/", status_code=303)

    return templates.TemplateResponse("login.html", {"request": request, "errors": [{"msg": "Invalid username or password"}]})


@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)


if __name__ == "__main__":
    uvicorn.run("views:app", reload=True)