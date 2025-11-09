from pydantic import BaseModel, EmailStr
from app.schemas.course import CourseOut

class StudentCreate(BaseModel):
    name: str
    email: EmailStr


class StudentOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    registeredCourses: list[CourseOut] | None = None  #  include their courses

    class Config:
        orm_mode = True
