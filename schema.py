from pydantic import BaseModel, Field


class Register_pyd_schema(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=3, max_length=255)
    pass_confirm: str = Field(..., min_length=3, max_length=255)


class Login_pyd_schema(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=3, max_length=255)
