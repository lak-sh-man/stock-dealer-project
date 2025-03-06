from pydantic import BaseModel, Field


class Register(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=2, max_length=255)


class Login(BaseModel):
    username: str
    password: str
