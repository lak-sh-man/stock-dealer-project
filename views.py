from setup import app


@app.get("/")
async def first_api():
    return {"message" : "Hello Eric!"}
