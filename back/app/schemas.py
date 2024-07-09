from pydantic import BaseModel, Field
from typing import Optional

class UserCreate(BaseModel):
    username: str
    password: str


    

class UserResponse(UserCreate):
    role: str = Field(default="admin")
    class Config:
        orm_mode = True


class UserUpdate(BaseModel):
    role: str
    username: str
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    #East: float
    #North: float
    longitude: float
    latitude: float
    #geom: str
    parameter1: float
    parameter2: float
    parameter3: float

class ProjectCreate(ProjectBase):
    pass
class ProjectUpdate(BaseModel):
    Parameter1: float
    Parameter2: float
    Parameter3: float


class Project(ProjectBase):
    class Config:
        orm_mode = True