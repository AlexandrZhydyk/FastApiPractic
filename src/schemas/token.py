from typing import List

from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenRead(BaseModel):
    scopes: List[str] = []
    email: EmailStr
    # id: int


class RefreshToken(BaseModel):
    refresh_token: str
