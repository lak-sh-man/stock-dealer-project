from setup import app, SessionLocal
from sqlalchemy.orm import Session
from typing import Annotated
from fastapi import Depends
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles


# tell fastapi the template location
templates = Jinja2Templates(directory="templates")


# Add session support (like Flask sessions)
app.add_middleware(SessionMiddleware, secret_key="lak-sh-man")

# tell fastapi the template location
app.mount("/static", StaticFiles(directory="static"), name="static")


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Annotated Dependency for DB Session
db_dependency = Annotated[Session, Depends(get_db)]