import uvicorn
from setup import app
import setup
from routes import home, auth_register, auth_login, logout, stocks




app.include_router(home.router)
app.include_router(auth_register.router)
app.include_router(auth_login.router)
app.include_router(logout.router)
app.include_router(stocks.router)
app.include_router(setup.router)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
