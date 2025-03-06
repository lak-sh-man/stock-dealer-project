import uvicorn
from setup import app, SessionLocal
from models import User
from schema import Register, Login
from pydantic import ValidationError

from fastapi import Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware
from fastapi.templating import Jinja2Templates

# Add session support (like Flask sessions)
app.add_middleware(SessionMiddleware, secret_key="your_secret_key")

# Setup Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@app.route("/register", methods=["GET", "POST"])
async def register(request: Request, db: Session = Depends(get_db)):
    if request.method == "POST":
        form = await request.form()
        username = form.get("username")
        password = form.get("password")

        user = User(username=username, password=password)
        db.add(user)
        db.commit()
        return RedirectResponse(url="/login", status_code=303)

    return templates.TemplateResponse("register.html", {"request": request})


@app.route("/login", methods=["GET", "POST"])
async def login(request: Request, db: Session = Depends(get_db)):
    if request.method == "POST":
        form = await request.form()
        username = form.get("username")
        password = form.get("password")

        user = db.query(User).filter(User.username == username).first()
        if user and user.password == password:
            request.session["session_user_id"] = user.id
            request.session["session_user_name"] = user.username
            return RedirectResponse(url="/", status_code=303)

        return HTMLResponse("Invalid username or password")

    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)


if __name__ == "__main__":
    uvicorn.run("views:app", reload=True)