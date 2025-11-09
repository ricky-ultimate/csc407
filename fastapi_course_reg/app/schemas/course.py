from pydantic import BaseModel

class CourseCreate(BaseModel):
    title: str
    code: str

class CourseOut(BaseModel):
    id: int
    title: str
    code: str
