from pydantic import BaseModel, EmailStr, ConfigDict

from .books import ReturnedBook


class SellerCreate(BaseModel):
    first_name: str
    last_name: str
    e_mail: EmailStr
    password: str


class SellerOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    e_mail: EmailStr

    class Config(ConfigDict):
        from_attributes = True


class SellerOutBooks(BaseModel):
    id: int
    first_name: str
    last_name: str
    e_mail: EmailStr
    books: list[ReturnedBook]

    class Config(ConfigDict):
        from_attributes = True
