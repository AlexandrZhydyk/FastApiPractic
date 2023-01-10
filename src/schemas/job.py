from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class JobCreate(BaseModel):
    email: EmailStr
    title: str
    description: str
    salary_from: int = Field(..., gt=0)
    salary_to: int = Field(..., gt=0)


class JobOut(JobCreate):
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda date: date.isoformat()[:-3] + 'Z'
        }


class JobUpdate(JobCreate):
    updated_at: datetime

    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda date: date.isoformat()[:-3] + 'Z'
        }