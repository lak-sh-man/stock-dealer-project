import uvicorn
from setup import app


@app.get("/")
async def first_api():
    return {"message" : "Hello Eric!"}


if __name__ == "__main__":
    uvicorn.run("views:app", reload=True)