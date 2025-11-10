from pydantic import BaseModel

class CourseCreate(BaseModel):
    title: str
    code: str
    units: int

class CourseOut(BaseModel):
    id: int
    title: str
    code: str
    units: int
