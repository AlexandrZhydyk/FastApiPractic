from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, validator, constr


class UserBase(BaseModel):
    email: EmailStr
    name: str
    is_company: bool
    is_active: bool


class UserOut(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda date: str(date)[:-3] + 'Z'
        }


class UserUpdate(BaseModel):
    id: Optional[int] = None
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    is_company: Optional[bool] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda date: str(date)[:-3] + 'Z'
        }


class UserCreate(UserBase):
    password: constr(min_length=8)
    confirmed_password: str

    @validator("confirmed_password")
    def match_passwords(cls, password, values, **kwargs):
        if "password" in values and values["password"] != password:
            raise ValueError("Please enter the same value for password and confirmed password field")
        return password

    class Config:
        orm_mode = True


class UserInDB(UserOut):
    hashed_password: str
